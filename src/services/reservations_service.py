from datetime import datetime
from sqlalchemy import text
from extensions import db
from services.booking_service import DATE_FMT


def list_reservations(q: str, customer_id: int | None, page: int, per_page: int):
    """
    Returns (rows, total, total_pages) for the reservation lookup.
    - If q is empty and customer_id is set -> only that customer's reservations.
    - If q is digits -> lookup by ReservationID.
    - Else -> lookup by email (exact and case-insensitive).
    - If q is empty and customer_id is None -> caller should render empty state.
    """
    offset = (page - 1) * per_page

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

    base_count = """
        SELECT COUNT(*) AS cnt
        FROM reservation r
        JOIN room rm     ON rm.RoomID = r.RoomID
        JOIN roomtype rt ON rt.RoomTypeID = rm.RoomTypeID
        JOIN customer c  ON c.CustomerID = r.CustomerID
    """

    where_clauses = []
    params = {}

    # If user is logged in & there is no query, logged in user's reservations will be displayed automatically
    if customer_id and not q:
        where_clauses.append("r.CustomerID = :cust")
        params["cust"] = customer_id
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
        return [], 0, 1

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    order_sql = " ORDER BY r.DateReserved DESC"
    limit_sql = " LIMIT :limit OFFSET :offset"

    # Count
    count_row = db.session.execute(
        text(base_count + where_sql),
        params
    ).mappings().first()
    total = int(count_row.cnt) if count_row else 0
    total_pages = max((total + per_page - 1) // per_page, 1)

    # Page
    page_params = dict(params)
    page_params.update({"limit": per_page, "offset": offset})

    rows = db.session.execute(
        text(base_select + where_sql + order_sql + limit_sql),
        page_params
    ).mappings().all()

    return rows, total, total_pages

def compute_totals(pending: dict):
    """
    Recompute totals on the server from the pending reservation dict.
    Returns (nights, subtotal, check_in_date, check_out_date).
    Raises ValueError if dates are invalid.
    """
    check_in = datetime.strptime(pending["check_in"], DATE_FMT).date()
    check_out = datetime.strptime(pending["check_out"], DATE_FMT).date()
    nights = (check_out - check_in).days
    price_per_night = float(pending["price_per_night"])
    subtotal = price_per_night * nights

    return nights, subtotal, check_in, check_out

def room_is_available(room_id: int, check_in_str: str, check_out_str: str) -> bool:
    """
    True if no overlapping CONFIRMED reservations exist for [check_in, check_out).
    Overlap: (existing.CheckIn < new.CheckOut) AND (existing.CheckOut > new.CheckIn)
    """
    row = db.session.execute(text("""
        SELECT COUNT(*) AS cnt
        FROM reservation
        WHERE RoomID = :room_id
          AND ReservationStatus = 'Confirmed'
          AND CheckInDate < :new_out
          AND CheckOutDate > :new_in
    """), {
        "room_id": room_id,
        "new_in":  check_in_str,
        "new_out": check_out_str,
    }).mappings().first()
    
    return (row and int(row.cnt) == 0)

def confirm_reservation(pending: dict, customer_id: int):
    """
    Insert a confirmed reservation. Returns the new ReservationID.
    """
    result = db.session.execute(text("""
        INSERT INTO reservation
            (CustomerID, RoomID, CheckInDate, CheckOutDate, NumberOfGuests, ReservationStatus)
        VALUES
            (:cust, :room, :in_date, :out_date, :guests, 'Confirmed')
    """), {
        "cust":     customer_id,
        "room":     pending["room_id"],
        "in_date":  pending["check_in"],
        "out_date": pending["check_out"],
        "guests":   pending["guests"],
    })
    db.session.commit()

    return result.lastrowid

def write_audit_log(customer_id: int, room_number: str, in_date: str, out_date: str):
    """
    Attempts Audit log. Let caller ignore failures.
    """
    db.session.execute(text("""
        INSERT INTO auditlog (CustomerID, Action, Description)
        VALUES (
          :cust,
          'Reservation Created',
          CONCAT('Reservation for room ', :roomnum, ' from ', :in_date, ' to ', :out_date)
        )
    """), {
        "cust":     customer_id,
        "roomnum":  room_number,
        "in_date":  in_date,
        "out_date": out_date,
    })
    db.session.commit()
