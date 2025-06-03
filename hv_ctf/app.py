from flask import Flask, request, redirect, url_for, render_template
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
        return render_template("index.html")

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
        return render_template("register.html")

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
        return render_template("login.html")

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
        return render_template("team_create.html")

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
        return render_template(
            "scoreboard.html",
            users=users,
            teams=teams,
        )

    @app.route("/challenges")
    @login_required
    def challenges():
        challenges = Challenge.query.all()
        return render_template("challenges.html", challenges=challenges)

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
        return render_template("solve.html", challenge=challenge)

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
