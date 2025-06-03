import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hv_ctf.app    import create_app
from hv_ctf.models import db, Challenge

# ── User-only solve test ────────────────────────────────────────────────────
def test_register_and_solve():
    app    = create_app({"TESTING": True})
    client = app.test_client()

    with app.app_context():
        chal = Challenge(name="easy", flag="flag{1}", points=100)
        db.session.add(chal); db.session.commit()
        chal_id = chal.id

    client.post("/register",
                data={"username": "alice", "password": "pw"},
                follow_redirects=True)
    client.post(f"/solve/{chal_id}",
                data={"flag": "flag{1}"},
                follow_redirects=True)

    resp = client.get("/scoreboard")
    assert b"alice: 100" in resp.data

# ── Team scoreboard test ───────────────────────────────────────────────────
def test_team_scoreboard():
    app    = create_app({"TESTING": True})
    client = app.test_client()

    with app.app_context():
        chal = Challenge(name="team", flag="flag{2}", points=50)
        db.session.add(chal); db.session.commit()
        chal_id = chal.id

    client.post("/register",       data={"username": "bob", "password": "pw"}, follow_redirects=True)
    client.post("/team/create",    data={"name": "red"},                      follow_redirects=True)
    client.post(f"/solve/{chal_id}", data={"flag": "flag{2}"},               follow_redirects=True)

    resp = client.get("/scoreboard")
    assert b"Team red: 50" in resp.data
    assert b"bob: 50"     in resp.data
