from careflow.models.user import User
from careflow.patterns.singleton import DatabaseManager


class UserRepository:
    def __init__(self, db_manager=None):
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
                user.role,
                user.password_hash,
                user.phone,
                user.created_at,
            ),
        )
        conn.commit()
        return user

    def get_by_id(self, user_id: str):
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
            role=row["role"],
            password_hash=row["password_hash"],
            phone=row["phone"] or "",
        )

    def get_by_email(self, email: str):
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
            role=row["role"],
            password_hash=row["password_hash"],
            phone=row["phone"] or "",
        )

    def list_by_role(self, role: str):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE role = ?", (role.upper(),))
        rows = cursor.fetchall()
        return [
            User(
                user_id=r["user_id"],
                name=r["name"],
                email=r["email"],
                role=r["role"],
                password_hash=r["password_hash"],
                phone=r["phone"] or "",
            )
            for r in rows
        ]
