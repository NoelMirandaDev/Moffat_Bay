from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from extensions import db
from services.rooms_service import (
    list_rooms_paginated,
    get_room_with_type,
    load_amenities,
)
from services.booking_service import (
    parse_and_validate_booking,
    build_pending_reservation,
    date_today,
    DATE_FMT,
    BookingValidationError,
)
from services.reservations_service import (
    list_reservations,
    compute_totals,
    room_is_available,
    confirm_reservation,
    write_audit_log,
)
from services.auth_service import (
    validate_registration,
    register_customer,
    authenticate_user,
    LoginError,
    RegistrationError,
)
from services.team_service import (
    save_team_message,
    get_team_with_contributions,
    get_team_member_with_contributions,
    TeamMessageError,
)
from models import TeamMember, TeamMemberContribution


def register_routes(app):
    """Registers all main routes for the Moffat Bay web application."""

    # Enable CSRF tokens in headers (important for fetch/AJAX)
    app.config["WTF_CSRF_HEADERS"] = ["X-CSRFToken", "X-CSRF-Token"]

    # ----------------
    # Landing Page
    # ----------------
    @app.route("/")
    def landing():
        return render_template("index.html")

    # -----------------
    # Attraction Page
    # -----------------
    @app.route("/attraction.html")
    def attraction():
        return render_template("attraction.html")

    # ---------------
    # About Us Page
    # ---------------
    @app.route("/about.html")
    def about():
        return render_template("about.html")

    # ------------------------
    # Lodge Reservation Page
    # ------------------------
    @app.route("/lodge_reservation.html")
    def lodge_reservation():
        try:
            page = int(request.args.get("page", 1))
        except ValueError:
            page = 1

        per_page = 3  # Rooms per page
        rooms, total_pages = list_rooms_paginated(page=page, per_page=per_page)

        return render_template(
            "lodge_reservation.html",
            rooms=rooms,
            page=page,
            total_pages=total_pages,
        )

    # -------------------------------
    # Team Profile Dynamic Page (Fixed)
    # -------------------------------
    @app.route("/team/<int:member_id>")
    def team_profile(member_id):
        """Renders a full 'book-style' page for each team member."""
        member = TeamMember.query.get_or_404(member_id)
        contributions = TeamMemberContribution.query.filter_by(
            team_member_id=member_id
        ).all()

        # ✅ FIX: Do not overwrite the SQLAlchemy relationship
        member_display = {
            "id": member.id,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "role": member.role,
            "bio": member.bio,
            "fun_fact": member.fun_fact,
            "linkedin_url": member.linkedin_url,
            "github_url": member.github_url,
            "email": member.email,
            "profile_image": member.profile_image,
            "contributions": [c.contribution for c in contributions],
        }

        return render_template("profile_base.html", member=member_display)

    # ---------------------------------
    # Room Details Page + Booking Step
    # ---------------------------------
    @app.route("/rooms/<int:room_id>", methods=["GET", "POST"])
    def room_details(room_id):
        room = get_room_with_type(room_id)

        if not room:
            flash("Room not found.", "error")
            return redirect(url_for("lodge_reservation"))

        if request.method == "POST":
            check_in_str = request.form.get("check_in", "")
            check_out_str = request.form.get("check_out", "")
            guests_str = request.form.get("guests", "")

            try:
                check_in, check_out, guests, nights = parse_and_validate_booking(
                    check_in_str, check_out_str, guests_str, room.MaxOccupancy
                )
            except BookingValidationError as e:
                flash(str(e), "error")
                return render_template(
                    "room_details.html",
                    room=room,
                    amenities=load_amenities(room_id),
                    today_str=date_today(),
                )

            session["pending_reservation"] = build_pending_reservation(
                room_row=room,
                check_in_str=check_in.strftime(DATE_FMT),
                check_out_str=check_out.strftime(DATE_FMT),
                guests=guests,
                nights=nights,
            )

            # Require login before confirming reservation
            if not session.get("customer_id"):
                flash(
                    "Please log in to continue your reservation.",
                    "error_login_modal",
                )
                return render_template(
                    "room_details.html",
                    room=room,
                    amenities=load_amenities(room_id),
                    show_login=True,
                    today_str=date_today(),
                )

            return redirect(url_for("reservation_summary"))

        # GET request
        return render_template(
            "room_details.html",
            room=room,
            amenities=load_amenities(room_id),
            today_str=date_today(),
        )

    # -------------------------
    # Reservation Lookup Page
    # -------------------------
    @app.route("/reservation_lookup.html", methods=["GET"])
    def reservation_lookup():
        q = (request.args.get("q") or "").strip()

        try:
            page = max(int(request.args.get("page", "1")), 1)
        except ValueError:
            page = 1

        per_page = 3
        customer_id = session.get("customer_id")

        if not q and not customer_id:
            return render_template(
                "reservation_lookup.html",
                q="",
                reservations=[],
                page=1,
                total_pages=1,
                total=0,
            )

        reservations, total, total_pages = list_reservations(
            q=q, customer_id=customer_id, page=page, per_page=per_page
        )

        return render_template(
            "reservation_lookup.html",
            q=q,
            reservations=reservations,
            page=page,
            total_pages=total_pages,
            total=total,
        )

    # --------------------------
    # Reservation Summary Page
    # --------------------------
    @app.route("/reservation_summary.html", methods=["GET", "POST"])
    def reservation_summary():
        pending = session.get("pending_reservation")

        if not pending:
            flash("No reservation in progress.", "error")
            return redirect(url_for("lodge_reservation"))

        # Must be logged in to confirm
        if not session.get("customer_id"):
            flash("Please log in to continue.", "error_login_modal")
            return redirect(url_for("landing", show_login=True))

        try:
            nights, subtotal = compute_totals(pending)
        except Exception:
            flash("Your reservation data is invalid. Please try again.", "error")
            session.pop("pending_reservation", None)
            return redirect(url_for("lodge_reservation"))

        if request.method == "POST":
            action = request.form.get("action")

            if action == "cancel":
                flash(
                    f"Reservation canceled for Room #{pending['room_number']}.",
                    "success",
                )
                session.pop("pending_reservation", None)
                return redirect(url_for("room_details", room_id=pending["room_id"]))

            if action == "confirm":
                if not room_is_available(
                    pending["room_id"], pending["check_in"], pending["check_out"]
                ):
                    flash(
                        "Sorry, this room is no longer available for those dates.",
                        "error",
                    )
                    return redirect(
                        url_for("room_details", room_id=pending["room_id"])
                    )

                try:
                    reservation_id = confirm_reservation(
                        pending, session["customer_id"]
                    )

                    # Write audit log (non-critical)
                    try:
                        write_audit_log(
                            customer_id=session["customer_id"],
                            room_number=pending["room_number"],
                            in_date=pending["check_in"],
                            out_date=pending["check_out"],
                        )
                    except Exception:
                        db.session.rollback()

                    session.pop("pending_reservation", None)
                    flash(
                        f"Your reservation #{reservation_id} has been confirmed! "
                        "Here are some attractions to explore during your stay.",
                        "success",
                    )
                    return redirect(url_for("attraction"))

                except Exception as e:
                    db.session.rollback()
                    flash(f"Failed to save reservation: {e}", "error")
                    return redirect(url_for("reservation_summary"))

        return render_template(
            "reservation_summary.html",
            reservation=pending,
            nights=nights,
            subtotal=subtotal,
        )

    # -------------------
    # Registration Page
    # -------------------
    @app.route("/registration", methods=["GET", "POST"])
    def registration():
        if request.method == "POST" and all(
            field in request.form
            for field in ["first", "last", "email", "password", "phone"]
        ):
            first = request.form["first"].strip()
            last = request.form["last"].strip()
            email = request.form["email"].strip()
            password = request.form["password"].strip()
            phone = request.form["phone"].strip()

            try:
                validate_registration(first, last, email, password, phone)
                register_customer(first, last, email, phone, password)
                flash("You have successfully registered.", "success_login_modal")
                return render_template("registration.html", show_login=True)

            except RegistrationError as e:
                flash(str(e), "error")
            except Exception:
                flash("Something went wrong, please try again.", "error")

        return render_template("registration.html")

    # ----------------
    # Login Page
    # ----------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "")
            password = request.form.get("password", "")

            try:
                customer = authenticate_user(email, password)
                session["customer_id"] = customer.CustomerID
                session["customer_email"] = customer.Email
                session["customer_phone"] = customer.Phone
                session["customer_firstName"] = customer.FirstName
                session["customer_lastName"] = customer.LastName

                if session.get("pending_reservation"):
                    return redirect(url_for("reservation_summary"))

                flash(f"Welcome back, {customer.FirstName}!", "success")

            except LoginError as e:
                flash(str(e), "error_login_modal")
                return render_template("index.html", show_login=True)
            except Exception:
                flash("Something went wrong. Please try again later.", "error_login_modal")
                return render_template("index.html", show_login=True)

        return redirect(url_for("landing"))

    # ----------------
    # Logout
    # ----------------
    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been successfully logged out.", "success")
        return redirect(url_for("landing"))

    # ---------------------------------------
    # TEAM FEATURES (About / Contact Section)
    # ---------------------------------------
    @app.route("/api/send-team-message", methods=["POST"])
    def send_team_message():
        """Handles POST requests for team contact form."""
        data = request.get_json()
        sender_name = data.get("senderName")
        sender_email = data.get("senderEmail")
        message = data.get("message")
        member_id = data.get("memberId")

        if not all([sender_name, sender_email, message, member_id]):
            return jsonify({"error": "Missing required fields."}), 400

        try:
            member_id = int(member_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid member ID."}), 400

        try:
            save_team_message(member_id, sender_name, sender_email, message)
            return jsonify({"success": True}), 200
        except TeamMessageError as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/team", methods=["GET"])
    def api_team():
        """Returns JSON for all team members and their contributions."""
        team = get_team_with_contributions()
        return jsonify(team)

    @app.route("/api/team/<int:member_id>", methods=["GET"])
    def api_team_member(member_id):
        """Returns JSON for a specific team member."""
        member = get_team_member_with_contributions(member_id)
        if not member:
            return jsonify({"error": "Team member not found"}), 404
        return jsonify(member)

    # --------------------
    # 404 Error Handler
    # --------------------
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404
