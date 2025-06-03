import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hv_ctf.app import create_app
from hv_ctf.models import db, Challenge


def test_register_and_solve():
    app = create_app({"TESTING": True})
    client = app.test_client()

    # ── Insert a dummy challenge ───────────────────────────────────────────
    with app.app_context():
        chal = Challenge(name="easy", flag="flag{1}", points=100)
        db.session.add(chal)
        db.session.commit()
        chal_id = chal.id

    # ── Register user ──────────────────────────────────────────────────────
    resp = client.post(
        "/register",
        data={"username": "alice", "password": "pw"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Hello alice" in resp.data

    # ── View challenges ────────────────────────────────────────────────────
    resp = client.get("/challenges")
    assert b"easy" in resp.data

    # ── Solve challenge ────────────────────────────────────────────────────
    resp = client.post(
        f"/solve/{chal_id}",
        data={"flag": "flag{1}"},
        follow_redirects=True,
    )
    assert b"alice: 100" in resp.data
