from typing import Optional, List
from careflow.models.user import User, UserRole
from careflow.patterns.singleton import DatabaseManager


class UserRepository:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create(self, user: User) -> User:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (user_id, name, email, role, password_hash, phone, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user.user_id,
                user.name,
                user.email,
                user.role.value if isinstance(user.role, UserRole) else str(user.role),
                user.password_hash,
                user.phone,
                user.created_at,
            ),
        )
        conn.commit()
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return User(
            user_id=row["user_id"],
            name=row["name"],
            email=row["email"],
            role=UserRole(row["role"]),
            password_hash=row["password_hash"],
            phone=row["phone"] or "",
            created_at=row["created_at"],
        )

    def get_by_email(self, email: str) -> Optional[User]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
        row = cursor.fetchone()
        if not row:
            return None
        return User(
            user_id=row["user_id"],
            name=row["name"],
            email=row["email"],
            role=UserRole(row["role"]),
            password_hash=row["password_hash"],
            phone=row["phone"] or "",
            created_at=row["created_at"],
        )

    def list_by_role(self, role: UserRole) -> List[User]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE role = ?", (role.value,))
        rows = cursor.fetchall()
        return [
            User(
                user_id=r["user_id"],
                name=r["name"],
                email=r["email"],
                role=UserRole(r["role"]),
                password_hash=r["password_hash"],
                phone=r["phone"] or "",
                created_at=r["created_at"],
            )
            for r in rows
        ]
