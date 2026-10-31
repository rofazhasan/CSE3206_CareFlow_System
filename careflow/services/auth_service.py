from careflow.models.user import User
from careflow.repositories.user_repository import UserRepository
import base64
import json
import time


class AuthService:
    def __init__(self, user_repo=None):
        self.user_repo = user_repo or UserRepository()

    def register_user(self, name: str, email: str, password: str, role: str, phone: str = "") -> User:
        clean_email = email.strip().lower()
        if not clean_email or "@" not in clean_email:
            raise ValueError("A valid email address is required.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if self.user_repo.get_by_email(clean_email):
            raise ValueError(f"User with email '{clean_email}' already exists.")

        hashed_password = User.hash_password(password)
        new_user = User(
            name=name.strip(),
            email=clean_email,
            role=str(role).upper(),
            password_hash=hashed_password,
            phone=phone.strip(),
        )
        return self.user_repo.create(new_user)

    def authenticate(self, email: str, password: str) -> dict:
        clean_email = email.strip().lower()
        user = self.user_repo.get_by_email(clean_email)
        if not user or not user.verify_password(password):
            raise ValueError("Invalid email or password credentials.")

        payload = {
            "sub": user.user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "exp": int(time.time()) + 3600,
        }
        token = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }

    def decode_token(self, token: str) -> dict:
        try:
            data = base64.b64decode(token.encode("utf-8")).decode("utf-8")
            payload = json.loads(data)
            return payload
        except Exception as e:
            raise ValueError(f"Invalid token: {str(e)}")
