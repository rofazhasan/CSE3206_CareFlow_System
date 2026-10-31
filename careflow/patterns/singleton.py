import sqlite3
import threading
from typing import Optional


class DatabaseManager:
    """
    Singleton Pattern (Creational Category).
    Ensures a single, thread-safe access point to the SQLite database.
    
    Problem Solved:
      Multiple direct database connections in multi-threaded application environments 
      can lead to file-lock collisions in SQLite, memory leaks, and inconsistent schema migrations.
    
    Alternative Rejected:
      Global Database Variable or passing connection everywhere:
      - Global variables pollute global scope and cannot encapsulate thread-safety locks.
      - Passing connection instances everywhere creates high coupling across layers.
    """
    _instance: Optional["DatabaseManager"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, db_path: str = "careflow.db") -> "DatabaseManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = "careflow.db"):
        if getattr(self, "_initialized", False):
            return
        self.db_path = db_path
        self._local = threading.local()
        self.init_schema()
        self._initialized = True

    def get_connection(self) -> sqlite3.Connection:
        """Returns a thread-local SQLite connection with dictionary-like row factory."""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._local.connection = conn
        return self._local.connection

    def close(self) -> None:
        """Closes thread-local connection."""
        if hasattr(self._local, "connection") and self._local.connection is not None:
            self._local.connection.close()
            self._local.connection = None

    def init_schema(self) -> None:
        """Initializes database tables if they do not exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            doctor_id TEXT NOT NULL,
            scheduled_time TEXT NOT NULL,
            reason TEXT NOT NULL,
            fee REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES users (user_id),
            FOREIGN KEY (doctor_id) REFERENCES users (user_id)
        );

        CREATE TABLE IF NOT EXISTS medical_records (
            record_id TEXT PRIMARY KEY,
            appointment_id TEXT UNIQUE NOT NULL,
            patient_id TEXT NOT NULL,
            doctor_id TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            notes TEXT,
            prescriptions_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id)
        );

        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            appointment_id TEXT UNIQUE NOT NULL,
            patient_id TEXT NOT NULL,
            base_amount REAL NOT NULL,
            discount_amount REAL NOT NULL,
            tax_amount REAL NOT NULL,
            total_payable REAL NOT NULL,
            status TEXT NOT NULL,
            payment_reference TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id)
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        conn.commit()

    @classmethod
    def reset_instance(cls) -> None:
        """Helper for unit test teardown to force a fresh singleton instance."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
            cls._instance = None
