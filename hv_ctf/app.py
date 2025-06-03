from flask import Flask


def create_app():
    """Create a minimal Flask application for the custom CTF platform."""
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "HV CTF platform"

    @app.route('/scoreboard')
    def scoreboard():
        # Placeholder scoreboard logic
        return "Scoreboard coming soon"

    # Register example plugins
    try:
        from hv_ctf.plugins.simple_scoreboard import bp as scoreboard_bp
        app.register_blueprint(scoreboard_bp)
    except Exception as exc:
        # Plugin import failed
        app.logger.debug("Plugin failed: %s", exc)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
