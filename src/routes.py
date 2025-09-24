from flask import render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db, csrf
from datetime import datetime
import re

# html <input type="date"> format
DATE_FMT = "%Y-%m-%d"


def register_routes(app):
    # Enable CSRF tokens in headers (important for fetch/AJAX)
    app.config["WTF_CSRF_HEADERS"] = ["X-CSRFToken", "X-CSRF-Token"]

    # --------------
    # Landing Page
    # --------------
    @app.route("/", endpoint="index")
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

        per_page = 3  # rooms per page
        offset = (page - 1) * per_page

        # Total rooms
        total = db.session.execute(text("SELECT COUNT(*) FROM room")).scalar() or 0

        total_pages = max((total + per_page - 1) // per_page, 1)

        rows = (
            db.session.execute(
                text(
                    """
                SELECT 
                    r.RoomID,
                    r.ADAAccessible,
                    r.ImagePath,
                    rt.TypeName,
                    rt.PricePerNight,
                    rt.MaxOccupancy
                FROM room r
                JOIN roomtype rt ON r.RoomTypeID = rt.RoomTypeID
                ORDER BY r.RoomNumber
                LIMIT :limit OFFSET :offset
            """
                ),
                {"limit": per_page, "offset": offset},
            )
            .mappings()
            .all()
        )

        return render_template(
            "lodge_reservation.html",
            rooms=rows,
            page=page,
            total_pages=total_pages,
        )

    # ---------------------------------
    # Room details Page + booking step
    # ---------------------------------
    @app.route("/rooms/<int:room_id>", methods=["GET", "POST"])
    def room_details(room_id):
        room = (
            db.session.execute(
                text(
                    """
                SELECT
                    r.RoomID,
                    r.RoomNumber,
                    r.ADAAccessible,
                    r.Description,
                    r.ImagePath,
                    rt.TypeName,
                    rt.PricePerNight,
                    rt.MaxOccupancy,
                    rt.BedConfiguration
                FROM room r
                JOIN roomtype rt ON r.RoomTypeID = rt.RoomTypeID
                WHERE r.RoomID = :r_id
            """
                ),
                {"r_id": room_id},
            )
            .mappings()
            .first()
        )

        if not room:
            flash("Room not found.", "error")
            return redirect(url_for("lodge_reservation"))

        if request.method == "POST":
            check_in_str = request.form.get("check_in", "").strip()
            check_out_str = request.form.get("check_out", "").strip()
            guests_str = request.form.get("guests", "").strip()

            # server-side date format validation
            try:
                check_in = datetime.strptime(check_in_str, DATE_FMT).date()
                check_out = datetime.strptime(check_out_str, DATE_FMT).date()
            except ValueError:
                flash("Please provide valid check-in and check-out dates.", "error")
                return render_template(
                    "room_details.html", room=room, amenities=_load_amenities(room_id)
                )

            if check_in >= check_out:
                flash("Check-out must be after check-in.", "error")
                return render_template(
                    "room_details.html", room=room, amenities=_load_amenities(room_id)
                )

            try:
                guests = int(guests_str)
            except ValueError:
                flash("Guests must be a whole number.", "error")
                return render_template(
                    "room_details.html", room=room, amenities=_load_amenities(room_id)
                )

            if guests < 1 or guests > room.MaxOccupancy:
                flash(f"Guests must be between 1 and {room.MaxOccupancy}.", "error")
                return render_template(
                    "room_details.html", room=room, amenities=_load_amenities(room_id)
                )

            # Computes nights and cost
            nights = (check_out - check_in).days
            nightly_rate = float(room.PricePerNight)
            subtotal = nightly_rate * nights

            # Saves pending reservation in session
            session["pending_reservation"] = {
                "room_id": room.RoomID,
                "room_type": room.TypeName,
                "price_per_night": nightly_rate,
                "max_occupancy": int(room.MaxOccupancy),
                "check_in": check_in_str,
                "check_out": check_out_str,
                "nights": nights,
                "guests": guests,
                "room_number": room.RoomNumber,
                "description": room.Description,
                "image_path": room.ImagePath,
            }

            # If not logged in, prompts user to log in or register; else redirected to reservation summary page
            if not session.get("customer_id"):
                flash("Please log in to continue your reservation.", "error")
                return render_template(
                    "room_details.html",
                    room=room,
                    amenities=_load_amenities(room_id),
                    show_login=True,
                )

            return redirect(url_for("reservation_summary"))

        # GET request: render page
        amenities = _load_amenities(room_id)
        return render_template("room_details.html", room=room, amenities=amenities)

    # -------------------------
    # Reservation Lookup Page
    # -------------------------
    @app.route("/reservation_lookup.html", methods=["GET"])
    def reservation_lookup():
        # Searches query (?q=). If empty and user is logged in, it shows their reservations.
        q = (request.args.get("q") or "").strip()

        # Page number (?page=). Sanitizes to a positive int; default = 1
        page_param = request.args.get("page", "1")
        try:
            page = max(int(page_param), 1)
        except ValueError:
            page = 1

        per_page = 3
        offset = (page - 1) * per_page

        # Reservation summary
        base_select = """
            SELECT
                r.ReservationID,
                r.CheckInDate,
                r.CheckOutDate,
                r.ReservationStatus,
                r.NumberOfGuests,
                r.DateReserved,
                rm.RoomNumber,
                rt.TypeName,
                rt.BedConfiguration,
                c.FirstName,
                c.LastName,
                c.Email
            FROM reservation r
            JOIN room rm     ON rm.RoomID = r.RoomID
            JOIN roomtype rt ON rt.RoomTypeID = rm.RoomTypeID
            JOIN customer c  ON c.CustomerID = r.CustomerID
        """

        # Number or reservations
        base_count = """
            SELECT COUNT(*) AS cnt
            FROM reservation r
            JOIN room rm     ON rm.RoomID = r.RoomID
            JOIN roomtype rt ON rt.RoomTypeID = rm.RoomTypeID
            JOIN customer c  ON c.CustomerID = r.CustomerID
        """

        # Dynamic WHERE depending on login state and query
        where_clauses = []
        params = {}

        if session.get("customer_id") and not q:
            # If user is logged in & there is no query, it shows only logged in user's reservations
            where_clauses.append("r.CustomerID = :cust")
            params["cust"] = session["customer_id"]
        elif q:
            # If q is digits, it is treated as a ReservationID. Otherwise, it treats it as an Email (case-insensitive exact)
            if q.isdigit():
                where_clauses.append("r.ReservationID = :rid")
                params["rid"] = int(q)
            else:
                where_clauses.append("LOWER(c.Email) = LOWER(:email)")
                params["email"] = q
        else:
            # If user not logged in and no query, it shows an empty page with a prompt to search
            return render_template(
                "reservation_lookup.html",
                q="",
                reservations=[],
                page=1,
                total_pages=1,
                total=0,
            )

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        order_sql = " ORDER BY r.DateReserved DESC"
        limit_sql = " LIMIT :limit OFFSET :offset"

        # Total count (for pagination)
        count_row = (
            db.session.execute(text(base_count + where_sql), params).mappings().first()
        )
        total = int(count_row.cnt) if count_row else 0

        # Total pages
        total_pages = max((total + per_page - 1) // per_page, 1)

        # Page data
        params_for_page = dict(params)
        params_for_page.update({"limit": per_page, "offset": offset})

        rows = (
            db.session.execute(
                text(base_select + where_sql + order_sql + limit_sql), params_for_page
            )
            .mappings()
            .all()
        )

        return render_template(
            "reservation_lookup.html",
            q=q,
            reservations=rows,
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
            flash("Please log in to continue.", "error")
            return redirect(url_for("landing", show_login=True))

        # Recompute totals on server
        try:
            check_in = datetime.strptime(pending["check_in"], DATE_FMT).date()
            check_out = datetime.strptime(pending["check_out"], DATE_FMT).date()
        except Exception:
            flash("Your reservation data is invalid. Please try again.", "error")
            session.pop("pending_reservation", None)
            return redirect(url_for("lodge_reservation"))

        nights = (check_out - check_in).days
        price_per_night = float(pending["price_per_night"])
        subtotal = price_per_night * nights

        if request.method == "POST":
            action = request.form.get("action")

            if action == "cancel":
                session.pop("pending_reservation", None)
                flash("Reservation canceled.", "success")
                return redirect(url_for("room_details", room_id=pending["room_id"]))

            if action == "confirm":
                if not _room_is_available(
                    pending["room_id"], pending["check_in"], pending["check_out"]
                ):
                    flash(
                        "Sorry, this room is no longer available for those dates.",
                        "error",
                    )
                    return redirect(url_for("room_details", room_id=pending["room_id"]))

                try:
                    db.session.execute(
                        text(
                            """
                            INSERT INTO reservation
                                (CustomerID, RoomID, CheckInDate, CheckOutDate, NumberOfGuests, ReservationStatus)
                            VALUES
                                (:cust, :room, :in_date, :out_date, :guests, 'Confirmed')
                        """
                        ),
                        {
                            "cust": session["customer_id"],
                            "room": pending["room_id"],
                            "in_date": pending["check_in"],
                            "out_date": pending["check_out"],
                            "guests": pending["guests"],
                        },
                    )
                    db.session.commit()

                    # Audit log
                    try:
                        db.session.execute(
                            text(
                                """
                                INSERT INTO auditlog (CustomerID, Action, Description)
                                VALUES (:cust, 'Reservation Created',
                                        CONCAT('Reservation for room ', :room_id,
                                            ' from ', :in_date, ' to ', :out_date))
                            """
                            ),
                            {
                                "cust": session["customer_id"],
                                "room_id": pending("room_id"),
                                "in_date": pending["check_in"],
                                "out_date": pending["check_out"],
                            },
                        )
                        db.session.commit()
                    except Exception:
                        db.session.rollback()  # prevents failing the booking if audit fails silently

                    session.pop("pending_reservation", None)
                    flash(
                        "Your reservation has been confirmed! Enjoy the available attractions.",
                        "success",
                    )
                    return redirect(url_for("attraction"))

                except Exception as e:
                    db.session.rollback()
                    flash(f"Failed to save reservation: {e}", "error")
                    return redirect(url_for("reservation_summary"))

        # GET: show summary
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
            k in request.form for k in ["first", "last", "email", "password", "phone"]
        ):
            first = request.form["first"]
            last = request.form["last"]
            email = request.form["email"]
            password = request.form["password"]
            phone = request.form["phone"]

            try:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    flash("Invalid email address", "error")
                elif not re.match(r"[A-Za-z]+$", first) or not re.match(
                    r"[A-Za-z]+$", last
                ):
                    flash("Name must only contain letters.", "error")
                elif not re.match(r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$", phone):
                    flash("Must be a valid US phone number.", "error")
                elif not re.match(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}", password):
                    flash(
                        "Password must contain at least 8 characters, contain uppercase, lowercase, and a number.",
                        "error",
                    )
                else:
                    result = db.session.execute(
                        text("SELECT * FROM customer WHERE email = :email"),
                        {"email": email},
                    ).fetchone()
                    if result:
                        flash("Email is already registered.", "error")
                    else:
                        pw_hash = generate_password_hash(password)
                        try:
                            db.session.execute(
                                text(
                                    "INSERT INTO customer (FirstName, LastName, Email, Phone, PasswordHash) VALUES (:first, :last, :email, :phone, :pw_hash)"
                                ),
                                {
                                    "first": first,
                                    "last": last,
                                    "email": email,
                                    "phone": phone,
                                    "pw_hash": pw_hash,
                                },
                            )
                            db.session.commit()
                            flash("You have successfully registered.", "success")
                        except Exception as e:
                            db.session.rollback()
                            print(f"Error: {e}")
                            flash("Database error. Please try again later.", "error")
            except Exception:
                flash("Something went wrong, please try again.", "error")
        return render_template("registration.html")

    # ------------
    # Login Page
    # ------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            customer = db.session.execute(
                text("SELECT * FROM customer WHERE Email = :email"), {"email": email}
            ).fetchone()

            if not customer or not check_password_hash(customer.PasswordHash, password):
                flash("Invalid email or password.", "error")
                return render_template("index.html", show_login=True)

            session["customer_id"] = customer.CustomerID
            session["customer_email"] = customer.Email
            session["customer_phone"] = customer.Phone
            session["customer_firstName"] = customer.FirstName
            session["customer_lastName"] = customer.LastName

            if session.get("pending_reservation"):
                return redirect(url_for("reservation_summary"))

            flash(f"Welcome back, {customer.FirstName}!", "success")

        return redirect(url_for("landing"))

    # ------------
    # Logout Route
    # ------------
    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been successfully logged out.", "success")
        return redirect(url_for("landing"))

    # ---------------------------------------
    # TEAM FEATURES OF ABOUT US / CONTACT US
    # ---------------------------------------

    # API: Send Team Message (CSRF Protected)
    @app.route("/api/send-team-message", methods=["POST"])
    def send_team_message():
        data = request.get_json()
        sender_name = data.get("senderName")
        sender_email = data.get("senderEmail")
        message = data.get("message")
        member_id = data.get("memberId")

        required_fields = [sender_name, sender_email, message, member_id]
        if not all(field and str(field).strip() for field in required_fields):
            return jsonify({"error": "Missing required fields."}), 400

        try:
            member_id_int = int(member_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid member ID."}), 400

        try:
            db.session.execute(
                text(
                    """
                    INSERT INTO team_message (team_member_id, sender_name, sender_email, message, sent_at)
                    VALUES (:member_id, :sender_name, :sender_email, :message, NOW())
                """
                ),
                {
                    "member_id": member_id_int,
                    "sender_name": sender_name,
                    "sender_email": sender_email,
                    "message": message,
                },
            )
            db.session.commit()
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # API: Get Team Members (improved to include fun_fact + contributions)
    @app.route("/api/team", methods=["GET"])
    def api_team():
        rows = (
            db.session.execute(
                text(
                    """
                SELECT id, first_name, middle_name, last_name, role, bio, fun_fact,
                       linkedin_url, github_url, email, profile_image
                FROM team_member
                ORDER BY id
            """
                )
            )
            .mappings()
            .all()
        )

        team = []
        for r in rows:
            contribs = (
                db.session.execute(
                    text(
                        "SELECT contribution FROM team_member_contribution WHERE team_member_id = :tid"
                    ),
                    {"tid": r.id},
                )
                .scalars()
                .all()
            )

            team.append(
                {
                    "id": r.id,
                    "first_name": r.first_name,
                    "middle_name": r.middle_name,
                    "last_name": r.last_name,
                    "role": r.role,
                    "bio": r.bio,
                    "fun_fact": r.fun_fact,
                    "linkedin_url": r.linkedin_url,
                    "github_url": r.github_url,
                    "email": r.email,
                    "profile_image": r.profile_image,
                    "contributions": contribs,
                }
            )

        return jsonify(team)

    # API: Get a single team member by ID
    @app.route("/api/team/<int:member_id>", methods=["GET"])
    def api_team_member(member_id):
        member = (
            db.session.execute(
                text(
                    """
                SELECT id, first_name, middle_name, last_name, role, bio, fun_fact,
                       linkedin_url, github_url, email, profile_image
                FROM team_member
                WHERE id = :id
            """
                ),
                {"id": member_id},
            )
            .mappings()
            .first()
        )

        if not member:
            return jsonify({"error": "Team member not found"}), 404

        contributions = (
            db.session.execute(
                text(
                    "SELECT contribution FROM team_member_contribution WHERE team_member_id = :id"
                ),
                {"id": member_id},
            )
            .scalars()
            .all()
        )

        return jsonify(
            {
                "id": member.id,
                "first_name": member.first_name,
                "middle_name": member.middle_name,
                "last_name": member.last_name,
                "role": member.role,
                "bio": member.bio,
                "fun_fact": member.fun_fact,
                "linkedin_url": member.linkedin_url,
                "github_url": member.github_url,
                "email": member.email,
                "profile_image": member.profile_image,
                "contributions": contributions,
            }
        )

    # ----------------------------
    # HELPER Functions Below
    # ----------------------------
    def _load_amenities(room_id: int):
        return (
            db.session.execute(
                text(
                    """
                SELECT a.AmenityID, a.Name
                FROM roomamenity ra
                JOIN amenity a ON a.AmenityID = ra.AmenityID
                WHERE ra.RoomID = :r_id
                ORDER BY a.Name
            """
                ),
                {"r_id": room_id},
            )
            .mappings()
            .all()
        )

    def _room_is_available(room_id: int, check_in: str, check_out: str) -> bool:
        row = (
            db.session.execute(
                text(
                    """
                SELECT COUNT(*) AS cnt
                FROM reservation
                WHERE RoomID = :room_id
                AND ReservationStatus = 'Confirmed'
                AND CheckInDate < :new_out
                AND CheckOutDate > :new_in
            """
                ),
                {"room_id": room_id, "new_in": check_in, "new_out": check_out},
            )
            .mappings()
            .first()
        )
        return row and int(row.cnt) == 0
