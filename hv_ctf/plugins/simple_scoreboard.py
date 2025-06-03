"""Example plugin demonstrating a custom scoreboard route."""
from flask import Blueprint

bp = Blueprint("simple_scoreboard", __name__)

@bp.route("/scoreboard")
def custom_scoreboard():
    # A trivial alternate view; replace / extend as desired.
    return "Custom scoreboard from plugin"
