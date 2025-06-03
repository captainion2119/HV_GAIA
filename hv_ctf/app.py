from flask import Flask, request, redirect, url_for, render_template_string
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    current_user,
)
from hv_ctf.models import db, User, Challenge, Solve


def create_app(test_config: dict | None = None):
    """Create a minimal Flask application for the custom CTF platform."""
    app = Flask(__name__)

    # ── Core config ───────────────────────────────────────────────────────────
    app.config.update(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    # ── Extensions ───────────────────────────────────────────────────────────
    db.init_app(app)
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # ── Routes ───────────────────────────────────────────────────────────────
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return f"Hello {current_user.username}!"
        return "HV CTF platform"

    # -- Auth ---------------------------------------------------------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if User.query.filter_by(username=username).first():
                return "User exists", 400
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("index"))
        return render_template_string(
            '<form method="post">Username: <input name="username"> '
            'Password: <input name="password" type="password">'
            '<input type="submit"></form>'
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                return "Invalid credentials", 400
            login_user(user)
            return redirect(url_for("index"))
        return render_template_string(
            '<form method="post">Username: <input name="username"> '
            'Password: <input name="password" type="password">'
            '<input type="submit"></form>'
        )

    # -- Scoreboard & Challenges -------------------------------------------
    @app.route("/scoreboard")
    def scoreboard():
        users = User.query.order_by(User.score.desc()).all()
        output = "\n".join(f"{u.username}: {u.score}" for u in users)
        return output or "No scores yet"

    @app.route("/challenges")
    @login_required
    def challenges():
        challenges = Challenge.query.all()
        links = "".join(
            f"<li><a href='{url_for('solve', chal_id=c.id)}'>{c.name}</a> "
            f"({c.points})</li>"
            for c in challenges
        )
        return f"<ul>{links}</ul>"

    @app.route("/solve/<int:chal_id>", methods=["GET", "POST"])
    @login_required
    def solve(chal_id: int):
        challenge = Challenge.query.get_or_404(chal_id)
        if request.method == "POST":
            if request.form["flag"] == challenge.flag:
                if not Solve.query.filter_by(
                    user_id=current_user.id, challenge_id=chal_id
                ).first():
                    solve = Solve(user_id=current_user.id, challenge_id=chal_id)
                    current_user.score += challenge.points
                    db.session.add(solve)
                    db.session.commit()
                return redirect(url_for("scoreboard"))
            return "Wrong flag", 400
        return render_template_string(
            "<form method='post'>Flag: <input name='flag'><input "
            "type='submit'></form>"
        )

    # ── Plugin system (blueprints) ──────────────────────────────────────────
    try:
        from hv_ctf.plugins.simple_scoreboard import bp as scoreboard_bp

        app.register_blueprint(scoreboard_bp)
    except Exception as exc:  # pragma: no cover
        app.logger.debug("Plugin failed: %s", exc)

    # ── DB bootstrap ────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":  # pragma: no cover
    create_app().run(debug=True)
