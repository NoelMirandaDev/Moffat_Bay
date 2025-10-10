from sqlalchemy import text
from extensions import db

def list_rooms_paginated(page: int, per_page: int):
    """
    Returns (rooms, total_pages) for the rooms listing.
    - rooms: list of mappings for the current page
    - total_pages: pages count derived from total rooms & per_page
    """
    # sanitizes inputs
    page = max(int(page or 1), 1)
    per_page = max(int(per_page or 1), 1)
    offset = (page - 1) * per_page

    total = db.session.execute(
        text("SELECT COUNT(*) FROM room")
    ).scalar() or 0

    total_pages = max((total + per_page - 1) // per_page, 1)

    rooms = db.session.execute(
        text("""
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
        """),
        {"limit": per_page, "offset": offset}
    ).mappings().all()

    return rooms, total_pages

def get_room_with_type(room_id: int):
    """
    Fetch a single room with its joined roomtype fields.
    Returns a mapping row or None.
    """
    return db.session.execute(
        text("""
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
        """),
        {"r_id": room_id},
    ).mappings().first()

def load_amenities(room_id: int):
    """
    Load amenities for a room as a list of mapping rows.
    """
    return db.session.execute(
        text("""
            SELECT a.AmenityID, a.Name
            FROM roomamenity ra
            JOIN amenity a ON a.AmenityID = ra.AmenityID
            WHERE ra.RoomID = :r_id
            ORDER BY a.Name
        """),
        {"r_id": room_id},
    ).mappings().all()
