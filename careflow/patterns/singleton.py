import sqlite3
import threading


class DatabaseManager:
    """
    Singleton Pattern (Creational Category).
    Ensures that only one shared database manager instance exists in the application.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_name="careflow.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance.db_name = db_name
                cls._instance.connection = None
                cls._instance.init_database()
        return cls._instance

    def get_connection(self):
        """Returns an active SQLite database connection with row access."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def init_database(self):
        """Creates the initial database tables if they do not exist."""
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

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    @classmethod
    def reset_instance(cls):
        """Helper to reset singleton instance between tests."""
        with cls._lock:
            if cls._instance:
                cls._instance.close()
            cls._instance = None
