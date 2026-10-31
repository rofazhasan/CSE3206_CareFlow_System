import hashlib
import uuid
from datetime import datetime


class User:
    def __init__(self, name: str, email: str, role: str, password_hash: str, phone: str = "", user_id: str = None):
        self.user_id = user_id or str(uuid.uuid4())[:8]
        self.name = name
        self.email = email.lower().strip()
        self.role = role.upper()  # PATIENT, DOCTOR, ADMIN, RECEPTIONIST
        self.password_hash = password_hash
        self.phone = phone
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def hash_password(password: str) -> str:
        """Simple, standard SHA-256 password hashing with salt."""
        salt = "ruet_cse3206"
        return hashlib.sha256((salt + password).encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        return self.password_hash == self.hash_password(password)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
            "created_at": self.created_at,
        }
