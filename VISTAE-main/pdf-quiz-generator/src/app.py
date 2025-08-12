from flask import Flask, request, jsonify
from flask_cors import CORS
from db.database import SessionLocal
from db.models import User
import bcrypt
from auth import authenticate_user

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for frontend-backend communication

# --------------------
# REGISTER ROUTE
# --------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    db = SessionLocal()
    # Check if email already exists
    if db.query(User).filter(User.email == email).first():
        db.close()
        return jsonify({"success": False, "message": "Email already registered"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(name=name, email=email, password_hash=hashed_password, role="student")
    db.add(new_user)
    db.commit()
    db.close()

    return jsonify({"success": True, "message": "User registered successfully"}), 200


# --------------------
# LOGIN ROUTE
# --------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    success, user_or_msg = authenticate_user(email, password)
    if not success:
        return jsonify({"success": False, "message": user_or_msg}), 400

    user = user_or_msg
    return jsonify({
        "success": True,
        "user": {
            "id": user.user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200


if __name__ == "__main__":
    app.run(debug=True)