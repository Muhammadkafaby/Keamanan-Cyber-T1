import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_students.db'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_crud_requires_login(client):
    resp = client.post("/add", data={"name": "Evil", "age": 20, "grade": "A"})
    assert resp.status_code in (302, 401, 403)

def test_crud_after_login(client):
    client.post("/login", data={"username": "admin", "password": "admin123"})
    resp = client.post("/add", data={"name": "Good", "age": 21, "grade": "B"})
    assert resp.status_code == 302
