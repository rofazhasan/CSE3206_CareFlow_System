from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import uuid


class UserRole(str, Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"
    RECEPTIONIST = "RECEPTIONIST"


@dataclass
class User:
    email: str
    name: str
    role: UserRole
    password_hash: str
    phone: str = ""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash raw password with SHA-256 and internal salt."""
        salt = "RUET_CSE3206_SALT_2026"
        return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Verify given plain password against stored hash."""
        return self.password_hash == self.hash_password(password)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value if isinstance(self.role, UserRole) else str(self.role),
            "phone": self.phone,
            "created_at": self.created_at,
        }
