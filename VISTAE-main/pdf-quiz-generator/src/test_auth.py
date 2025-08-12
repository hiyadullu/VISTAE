from auth import register_user, authenticate_user

def test_register_login():
    # Register a user
    success, msg = register_user("Alice", "alice@example.com", "mypassword")
    print("Register:", success, msg)

    # Try login
    success, user_or_msg = authenticate_user("alice@example.com", "mypassword")
    if success:
        print("Login successful:", user_or_msg.name, user_or_msg.email)
    else:
        print("Login failed:", user_or_msg)

if __name__ == "__main__":
    test_register_login()