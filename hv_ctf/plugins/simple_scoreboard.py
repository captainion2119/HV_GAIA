"""Example plugin for customizing the scoreboard."""

from flask import Blueprint

bp = Blueprint("simple_scoreboard", __name__)


@bp.route("/scoreboard")
def custom_scoreboard():
    # Example scoreboard output
    return "Custom scoreboard from plugin"
