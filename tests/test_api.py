from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health(): assert c.get("/health").json()["status"]=="ok"
def test_grounded_flow():
 c.post("/api/seed"); r=c.post("/api/ask",json={"question":"Which project is behind schedule?"}); assert r.status_code==200 and r.json()["grounded"]
