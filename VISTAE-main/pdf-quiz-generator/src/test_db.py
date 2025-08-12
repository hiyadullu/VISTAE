from db.database import SessionLocal
from db.models import User

def test_db():
    db = SessionLocal()

    # Create a new user
    new_user = User(
        name="Test User",
        email="testuser@example.com",
        password_hash="hashedpassword123",
        role="student"
    )
    db.add(new_user)
    db.commit()

    # Fetch all users and print
    users = db.query(User).all()
    print("All users in database:")
    for user in users:
        print(f"ID: {user.user_id}, Name: {user.name}, Email: {user.email}, Role: {user.role}")

    db.close()

if __name__ == "__main__":
    test_db()