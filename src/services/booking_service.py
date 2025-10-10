from datetime import datetime, date

DATE_FMT = "%Y-%m-%d"

class BookingValidationError(Exception):
    """Raised when user-submitted booking data is invalid."""

def parse_and_validate_booking(check_in_str: str, check_out_str: str, guests_str: str, max_occupancy: int):
    """
    Parse strings from the form, validate dates and guest count.
    Returns (check_in_date, check_out_date, guests_int, nights).
    Raises BookingValidationError with a user-friendly message on error.
    """
    # Dates
    try:
        check_in = datetime.strptime(check_in_str.strip(), DATE_FMT).date()
        check_out = datetime.strptime(check_out_str.strip(), DATE_FMT).date()
    except ValueError:
        raise BookingValidationError("Please provide valid check-in and check-out dates.")
    
    today = date.today()

    if check_in < today:
        raise BookingValidationError("Check-in cannot be in the past.")
    if check_out < today:
        raise BookingValidationError("Check-out cannot be in the past.")

    if check_in >= check_out:
        raise BookingValidationError("Check-out must be after check-in.")

    # Guests
    try:
        guests = int(guests_str.strip())
    except ValueError:
        raise BookingValidationError("Guests must be a whole number.")

    if guests < 1 or guests > int(max_occupancy):
        raise BookingValidationError(f"Guests must be between 1 and {max_occupancy}.")

    nights = (check_out - check_in).days
    return check_in, check_out, guests, nights

def build_pending_reservation(room_row, check_in_str: str, check_out_str: str, guests: int, nights: int):
    """
    Build the dict we keep in session for the 'pending_reservation'.
    """
    nightly_rate = float(room_row.PricePerNight)
    return {
        "room_id":         room_row.RoomID,
        "room_type":       room_row.TypeName,
        "price_per_night": nightly_rate,
        "max_occupancy":   int(room_row.MaxOccupancy),
        "check_in":        check_in_str,
        "check_out":       check_out_str,
        "nights":          nights,
        "guests":          guests,
        "room_number":     room_row.RoomNumber,
        "description":     room_row.Description,
        "image_path":      room_row.ImagePath,
    }

def date_today():
    """
    Returns today's date in string format [%Y-%m-%d]
    """
    return date.today().strftime(DATE_FMT)
