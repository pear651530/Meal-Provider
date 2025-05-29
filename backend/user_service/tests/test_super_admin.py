import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext

from ..main import app, get_db, pwd_context
from ..models import Base, User, DiningRecord, Review, Notification
from ..database import DATABASE_URL

# Override the database URL for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the database dependency and URL
app.dependency_overrides[get_db] = override_get_db
app.state.database_url = TEST_DATABASE_URL

client = TestClient(app)

def init_test_db():
    """Initialize the test database with all required tables"""
    # Drop all tables if they exist
    Base.metadata.drop_all(bind=engine)
    
    # Ensure all models are registered
    for model in [User, DiningRecord, Review, Notification]:
        if not hasattr(model, '__tablename__'):
            raise ValueError(f"Model {model.__name__} is missing __tablename__")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Created tables: {tables}")  # Debug print
    
    # Check for all required tables
    required_tables = ["users", "dining_records", "reviews", "notifications"]
    missing_tables = [table for table in required_tables if table not in tables]
    if missing_tables:
        raise AssertionError(f"Missing tables: {missing_tables}. Available tables: {tables}")

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment before any tests run"""
    # Override the database URL
    import user_service.database
    user_service.database.DATABASE_URL = TEST_DATABASE_URL
    yield

@pytest.fixture(scope="function")
def db():
    # Initialize database
    init_test_db()
    
    # Create a database session
    db = TestingSessionLocal()
    try:
        # Create super admin if it doesn't exist
        super_admin = db.query(User).filter(User.role == "super_admin").first()
        if not super_admin:
            hashed_password = pwd_context.hash("superadmin123")
            super_admin = User(
                username="superadmin",
                hashed_password=hashed_password,
                role="super_admin"
            )
            db.add(super_admin)
            db.commit()
        yield db
    finally:
        db.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)

def create_test_user(username: str, password: str, role: str = "employee", db=None):
    response = client.post(
        "/users/",
        json={"username": username, "password": password}
    )
    if response.status_code == 200 and role != "employee":
        # Update role if needed
        super_admin_token = get_super_admin_token()
        client.put(
            f"/users/{response.json()['id']}/role",
            params={"new_role": role},
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
    return response

def get_super_admin_token():
    response = client.post(
        "/token",
        data={"username": "superadmin", "password": "superadmin123"}
    )
    return response.json()["access_token"]

def get_user_token(username: str, password: str):
    response = client.post(
        "/token",
        data={"username": username, "password": password}
    )
    return response.json()["access_token"]

def test_super_admin_creation(db):
    """Test that super admin is created on startup"""
    # The super admin should be created automatically on startup
    response = client.post(
        "/token",
        data={"username": "superadmin", "password": "superadmin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_role_update_by_super_admin(db):
    """Test that super admin can update user roles"""
    # Create a regular user
    create_test_user("testuser", "testpass")
    
    # Get super admin token
    super_admin_token = get_super_admin_token()
    
    # Get the user's ID
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {get_user_token('testuser', 'testpass')}"}
    )
    user_id = response.json()["id"]
    
    # Update user role to admin
    response = client.put(
        f"/users/{user_id}/role",
        params={"new_role": "admin"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

def test_role_update_by_non_super_admin(db):
    """Test that non-super admin cannot update user roles"""
    # Create two regular users
    create_test_user("user1", "pass1")
    create_test_user("user2", "pass2")
    
    # Get user1's token
    user1_token = get_user_token("user1", "pass1")
    
    # Get user2's ID
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {get_user_token('user2', 'pass2')}"}
    )
    user2_id = response.json()["id"]
    
    # Try to update user2's role
    response = client.put(
        f"/users/{user2_id}/role",
        params={"new_role": "admin"},
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 403

def test_invalid_role_update(db):
    """Test that invalid roles are rejected"""
    # Create a regular user
    create_test_user("testuser", "testpass")
    
    # Get super admin token
    super_admin_token = get_super_admin_token()
    
    # Get the user's ID
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {get_user_token('testuser', 'testpass')}"}
    )
    user_id = response.json()["id"]
    
    # Try to update to invalid role
    response = client.put(
        f"/users/{user_id}/role",
        params={"new_role": "invalid_role"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 400

def test_cannot_modify_super_admin(db):
    """Test that super admin's role cannot be modified"""
    # Get super admin token
    super_admin_token = get_super_admin_token()
    
    # Get super admin's ID
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    super_admin_id = response.json()["id"]
    
    # Try to modify super admin's role
    response = client.put(
        f"/users/{super_admin_id}/role",
        params={"new_role": "admin"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 403

def test_update_nonexistent_user(db):
    """Test updating role of non-existent user"""
    # Get super admin token
    super_admin_token = get_super_admin_token()
    
    # Try to update non-existent user
    response = client.put(
        "/users/99999/role",
        params={"new_role": "admin"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 404 