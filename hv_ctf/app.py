from flask import Flask, request, redirect, url_for, render_template_string
from flask_login import LoginManager, login_user, login_required, current_user
from hv_ctf.models import db, User, Challenge, Solve, Team


def create_app(test_config: dict | None = None):
    """Create a minimal Flask application for the custom CTF platform."""
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return f"Hello {current_user.username}!"
        return "HV CTF platform"

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
            '<form method="post">Username: <input name="username"> Password: <input name="password" type="password"><input type="submit"></form>'
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
            '<form method="post">Username: <input name="username"> Password: <input name="password" type="password"><input type="submit"></form>'
        )

    @app.route("/team/create", methods=["GET", "POST"])
    @login_required
    def create_team():
        if request.method == "POST":
            name = request.form["name"]
            if Team.query.filter_by(name=name).first():
                return "Team exists", 400
            team = Team(name=name)
            db.session.add(team)
            db.session.commit()
            current_user.team = team
            db.session.commit()
            return redirect(url_for("scoreboard"))
        return render_template_string(
            '<form method="post">Team name: <input name="name"><input type="submit"></form>'
        )

    @app.route("/team/join/<int:team_id>")
    @login_required
    def join_team(team_id: int):
        team = Team.query.get_or_404(team_id)
        current_user.team = team
        db.session.commit()
        return redirect(url_for("scoreboard"))

    @app.route("/scoreboard")
    def scoreboard():
        users = User.query.order_by(User.score.desc()).all()
        teams = Team.query.order_by(Team.score.desc()).all()
        user_lines = "\n".join(f"{u.username}: {u.score}" for u in users)
        team_lines = "\n".join(f"Team {t.name}: {t.score}" for t in teams)
        output = "\n".join(filter(None, [team_lines, user_lines]))
        return output or "No scores yet"

    @app.route("/challenges")
    @login_required
    def challenges():
        challenges = Challenge.query.all()
        links = "".join(
            f"<li><a href='{url_for('solve', chal_id=c.id)}'>{c.name}</a> ({c.points})</li>"
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
                    if current_user.team:
                        current_user.team.score += challenge.points
                    db.session.add(solve)
                    db.session.commit()
                return redirect(url_for("scoreboard"))
            return "Wrong flag", 400
        return render_template_string(
            "<form method='post'>Flag: <input name='flag'><input type='submit'></form>"
        )

    with app.app_context():
        db.create_all()

    # Register example plugins
    try:
        from hv_ctf.plugins.simple_scoreboard import bp as scoreboard_bp

        app.register_blueprint(scoreboard_bp)
    except Exception as exc:
        # Plugin import failed
        app.logger.debug("Plugin failed: %s", exc)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
