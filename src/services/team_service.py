from extensions import db
from sqlalchemy import text

class TeamMessageError(Exception):
    """Raised when sending a team message fails."""

def save_team_message(member_id: int, sender_name: str, sender_email: str, message: str):
    """
    Inserts a team message into the database.
    Raises TeamMessageError if something goes wrong.
    """
    try:
        db.session.execute(
            text("""
                INSERT INTO team_message (team_member_id, sender_name, sender_email, message, sent_at)
                VALUES (:member_id, :sender_name, :sender_email, :message, NOW())
            """),
            {
                "member_id": member_id,
                "sender_name": sender_name,
                "sender_email": sender_email,
                "message": message,
            },
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise TeamMessageError(str(e))

def get_team_with_contributions():
    """
    Returns a list of team members, each with their contributions array.
    Shape:
    [
      {
        "id": 1,
        "first_name": "...",
        "middle_name": "...",
        "last_name": "...",
        "role": "...",
        "bio": "...",
        "fun_fact": "...",
        "linkedin_url": "...",
        "github_url": "...",
        "email": "...",
        "profile_image": "...",
        "contributions": ["...", "..."]
      },
      ...
    ]
    """
    # Fetches team members
    member_rows = (
        db.session.execute(
            text("""
                SELECT id, first_name, middle_name, last_name, role, bio, fun_fact,
                       linkedin_url, github_url, email, profile_image
                FROM team_member
                ORDER BY id
            """)
        )
        .mappings()
        .all()
    )

    team = []
    for member in member_rows:
        # Fetches team member's contributions
        contribution_rows = (
            db.session.execute(
                text("""
                    SELECT contribution
                    FROM team_member_contribution
                    WHERE team_member_id = :tid
                """),
                {"tid": member.id},
            )
            .scalars()
            .all()
        )

        team.append({
            "id":            member.id,
            "first_name":    member.first_name,
            "middle_name":   member.middle_name,
            "last_name":     member.last_name,
            "role":          member.role,
            "bio":           member.bio,
            "fun_fact":      member.fun_fact,
            "linkedin_url":  member.linkedin_url,
            "github_url":    member.github_url,
            "email":         member.email,
            "profile_image": member.profile_image,
            "contributions": contribution_rows,
        })

    return team

def get_team_member_with_contributions(member_id: int):
    """
    Return a single team member and their contributions by ID.
    Raises None if not found.
    """
    # Fetches the team member
    member_row = (
        db.session.execute(
            text("""
                SELECT id, first_name, middle_name, last_name, role, bio, fun_fact,
                       linkedin_url, github_url, email, profile_image
                FROM team_member
                WHERE id = :id
            """),
            {"id": member_id},
        )
        .mappings()
        .first()
    )

    if not member_row:
        return None

    # Fetches contributions for this member
    contribution_rows = (
        db.session.execute(
            text("""
                SELECT contribution
                FROM team_member_contribution
                WHERE team_member_id = :id
            """),
            {"id": member_id},
        )
        .scalars()
        .all()
    )

    return {
        "id":            member_row.id,
        "first_name":    member_row.first_name,
        "middle_name":   member_row.middle_name,
        "last_name":     member_row.last_name,
        "role":          member_row.role,
        "bio":           member_row.bio,
        "fun_fact":      member_row.fun_fact,
        "linkedin_url":  member_row.linkedin_url,
        "github_url":    member_row.github_url,
        "email":         member_row.email,
        "profile_image": member_row.profile_image,
        "contributions": contribution_rows,
    }
