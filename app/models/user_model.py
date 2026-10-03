from werkzeug.security import generate_password_hash, check_password_hash
from app.db import execute_query

class UserModel:
    @staticmethod
    def create_user(username, email, password):
        """Creates a new user with securely hashed password."""
        hashed_password = generate_password_hash(password, method='scrypt')
        sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
        user_id = execute_query(sql, (username, email, hashed_password), commit=True)
        return user_id

    @staticmethod
    def get_by_email(email):
        """Fetches user by email address."""
        sql = "SELECT * FROM users WHERE email = %s"
        return execute_query(sql, (email,), fetch_one=True)

    @staticmethod
    def get_by_username(username):
        """Fetches user by username."""
        sql = "SELECT * FROM users WHERE username = %s"
        return execute_query(sql, (username,), fetch_one=True)

    @staticmethod
    def get_by_id(user_id):
        """Fetches user by user ID."""
        sql = "SELECT id, username, email, created_at FROM users WHERE id = %s"
        return execute_query(sql, (user_id,), fetch_one=True)

    @staticmethod
    def verify_password(stored_password_hash, password_input):
        """Verifies input password against stored hash."""
        return check_password_hash(stored_password_hash, password_input)

    @staticmethod
    def update_profile(user_id, username, email):
        """Updates user profile information."""
        sql = "UPDATE users SET username = %s, email = %s WHERE id = %s"
        execute_query(sql, (username, email, user_id), commit=True)

    @staticmethod
    def update_password(user_id, new_password):
        """Updates user password with secure hash."""
        hashed_password = generate_password_hash(new_password, method='scrypt')
        sql = "UPDATE users SET password_hash = %s WHERE id = %s"
        execute_query(sql, (hashed_password, user_id), commit=True)
