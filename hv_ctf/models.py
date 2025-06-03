"""Database models for the HV CTF platform."""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ── Team --------------------------------------------------------------------
class Team(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(80), unique=True, nullable=False)
    score = db.Column(db.Integer, default=0)

# ── User --------------------------------------------------------------------
class User(db.Model, UserMixin):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    score         = db.Column(db.Integer, default=0)

    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    team    = db.relationship("Team", backref="members")

    # Helpers
    def set_password(self, pw: str) -> None:
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        return check_password_hash(self.password_hash, pw)

# ── Challenge & Solve -------------------------------------------------------
class Challenge(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    name   = db.Column(db.String(120), nullable=False)
    flag   = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, default=0)

class Solve(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("user.id"))
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenge.id"))
    db.UniqueConstraint(user_id, challenge_id)
