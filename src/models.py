from extensions import db


class TeamMember(db.Model):
    """
    Stores core information about each team member.
    """

    __tablename__ = "team_member"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    fun_fact = db.Column(db.Text)
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    email = db.Column(db.String(100))
    profile_image = db.Column(db.String(255))

    # One-to-many relationship: a member can have multiple contributions
    contributions = db.relationship(
        "TeamMemberContribution", backref="member", cascade="all, delete-orphan"
    )

class TeamMemberContribution(db.Model):
    """
    Stores individual contributions for each team member.
    """

    __tablename__ = "team_member_contribution"

    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(
        db.Integer, db.ForeignKey("team_member.id"), nullable=False
    )
    contribution = db.Column(db.Text, nullable=False)
