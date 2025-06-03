import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hv_ctf.app import create_app

def test_index():
    app = create_app()
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
    assert b"HV CTF platform" in resp.data
