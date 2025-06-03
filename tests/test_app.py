import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hv_ctf.app import create_app
from hv_ctf.models import db, Challenge, User, Team


def test_register_and_solve():
    app = create_app({"TESTING": True})
    client = app.test_client()
    with app.app_context():
        db.create_all()
        chal = Challenge(name="easy", flag="flag{1}", points=100)
        db.session.add(chal)
        db.session.commit()
        chal_id = chal.id

    resp = client.post(
        "/register", data={"username": "alice", "password": "pw"}, follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"Hello alice" in resp.data

    resp = client.get("/challenges")
    assert b"easy" in resp.data

    resp = client.post(
        f"/solve/{chal_id}", data={"flag": "flag{1}"}, follow_redirects=True
    )
    assert b"alice: 100" in resp.data


def test_team_scoreboard():
    app = create_app({"TESTING": True})
    client = app.test_client()
    with app.app_context():
        db.create_all()
        chal = Challenge(name="team", flag="flag{2}", points=50)
        db.session.add(chal)
        db.session.commit()
        chal_id = chal.id

    client.post("/register", data={"username": "alice", "password": "pw"}, follow_redirects=True)
    client.post("/team/create", data={"name": "red"}, follow_redirects=True)
    resp = client.post(f"/solve/{chal_id}", data={"flag": "flag{2}"}, follow_redirects=True)
    assert b"Team red: 50" in resp.data
    assert b"alice: 50" in resp.data
