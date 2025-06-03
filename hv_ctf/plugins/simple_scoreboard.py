"""Example plugin demonstrating a custom scoreboard route."""
from flask import Blueprint

bp = Blueprint("simple_scoreboard", __name__)

@bp.route("/scoreboard")
def custom_scoreboard():
    # A trivial alternative output; replace or extend as desired.
    return "Custom scoreboard from plugin"
