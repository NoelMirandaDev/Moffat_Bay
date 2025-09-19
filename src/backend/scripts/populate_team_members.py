# scripts/populate_team_members.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app import create_app
from extensions import db
from models import TeamMember, TeamMemberContribution

def main():
    app = create_app()
    with app.app_context():
        # Clear existing data (optional)
        TeamMemberContribution.query.delete()
        TeamMember.query.delete()
        db.session.commit()

        # --- TEAM MEMBERS DATA ---
        team_members = [
            {
                "first_name": "Noel",
                "middle_name": "Yobani",
                "last_name": "Miranda",
                "role": "Project Manager and Full Stack Developer",
                "bio": (
                    "With a passion for continuous growth, I am currently completing my third bachelor’s degree in Software Development at Bellevue University, graduating in October 2025. "
                    "I also hold bachelor’s degrees in Sociology and Criminal Justice and recently served as a backend software engineering intern at SuperFile.\n\n"
                    "My expertise is in web development with a strong focus on security, and within this project my role as project manager and full stack developer centers on backend development while guiding the team’s progress.\n\n"
                    "I am committed to lifelong learning, seeking challenges that strengthen my technical abilities and collaborative skills."
                ),
                "fun_fact": "Outside of coding, I enjoy exploring the wilderness with my fiancé, where we find inspiration and balance through hiking and connecting with nature.",
                "linkedin_url": "https://www.linkedin.com/in/nymirandadev",
                "github_url": "https://github.com/NoelMirandaDev",
                "email": "nymiranda.dev@gmail.com",
                "profile_image": "Noel_profile.jpg",
                "contributions": [
                    "Implemented user Login system",
                    "Initialized the Moffat Bay GitHub repository and project structure",
                    "Implemented the room reservation system"
                ]
            },
            {
                "first_name": "Kyle",
                "middle_name": "James",
                "last_name": "Marlia-Conner",
                "role": "Developer",
                "bio": (
                    "Kyle is a dedicated developer with a strong background in full stack web development.\n\n"
                    "He brings attention to detail and a collaborative spirit to the team, ensuring project components are robust, scalable, and user-friendly."
                ),
                "fun_fact": "Kyle is an amateur chef who loves experimenting with new recipes and enjoys mountain biking on weekends.",
                "linkedin_url": None,
                "github_url": None,
                "email": None,
                "profile_image": "Kyle_profile.jpg",
                "contributions": [
                    "Contributed to backend API development",
                    "Implemented front-end UI enhancements",
                    "Reviewed and improved code for scalability"
                ]
            },
            {
                "first_name": "Steve",
                "middle_name": None,
                "last_name": "Stylin",
                "role": "Database Designer, Frontend & Backend Developer",
                "bio": (
                    "Steve was born in Haiti and holds a degree in Computer Science. She began her career as an Analyst Programmer for four years before being promoted to Junior Database Administrator, and three years later advancing to Senior DBA in Haiti.\n\n"
                    "Currently, Steve is expanding her expertise at Bellevue University, pursuing studies in Software Development to gain a broader perspective in the field."
                ),
                "fun_fact": "Steve loves hiking and camping. Her favorite authors include Eckhart Tolle, Stephen King, Edgar Allan Poe, and Nicholas Sparks. She is also fascinated by Egyptian history.",
                "linkedin_url": None,
                "github_url": "https://github.com/sstylin",
                "email": None,
                "profile_image": "Steve_profile.JPG",
                "contributions": [
                    "Created the Technical Design Document (TDD) for the project",
                    "Created the Entity Relationship Diagram (ERD) for the application database",
                    "Developed the backend of the landing page",
                    "Leading the development of the About Us page (frontend and backend)"
                ]
            },
            {
                "first_name": "Riese",
                "middle_name": None,
                "last_name": "Bohnak",
                "role": "Developer",
                "bio": (
                    "Riese is an innovative developer who excels at solving complex technical problems and bringing creative solutions to the team.\n\n"
                    "Their adaptability and dedication help ensure project milestones are met."
                ),
                "fun_fact": "Riese enjoys spending time with his family and loves running.",
                "linkedin_url": None,
                "github_url": "https://github.com/Rojo234",
                "email": None,
                "profile_image": "Riese_profile.jpg",
                "contributions": [
                    "Registration Page Functional Test",
                    "Reservation Summary page Frontend",
                    "Registration Page Frontend & Backend"
                ]
            },
            {
                "first_name": "Amit",
                "middle_name": None,
                "last_name": "Rizal",
                "role": "Developer",
                "bio": (
                    "Amit is a meticulous software developer with a keen interest in both backend and frontend technologies.\n\n"
                    "He is known for his problem-solving skills and strong teamwork."
                ),
                "fun_fact": "Amit is an avid traveler who has visited more than 15 countries and loves photography.",
                "linkedin_url": None,
                "github_url": None,
                "email": None,
                "profile_image": "Amit_profile.jpg",
                "contributions": [
                    "Implemented responsive web layouts",
                    "Contributed bug fixes and performance improvements",
                    "Enhanced accessibility features"
                ]
            }
        ]

        # Insert team members and contributions
        for member_data in team_members:
            member = TeamMember(
                first_name=member_data["first_name"],
                middle_name=member_data["middle_name"],
                last_name=member_data["last_name"],
                role=member_data["role"],
                bio=member_data["bio"],
                fun_fact=member_data["fun_fact"],
                linkedin_url=member_data["linkedin_url"],
                github_url=member_data["github_url"],
                email=member_data["email"],
                profile_image=member_data["profile_image"]
            )
            db.session.add(member)
            db.session.flush()  # To get member.id

            for contrib in member_data["contributions"]:
                db.session.add(TeamMemberContribution(
                    team_member_id=member.id,
                    contribution=contrib
                ))

        db.session.commit()
        print("Team members and contributions added to database.")

if __name__ == "__main__":
    main()