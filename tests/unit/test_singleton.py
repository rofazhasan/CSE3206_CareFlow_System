import os
import tempfile
import threading
from careflow.patterns.singleton import DatabaseManager


def test_singleton_unique_instance():
    DatabaseManager.reset_instance()
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db1 = DatabaseManager(tmp.name)
        db2 = DatabaseManager(tmp.name)
        assert db1 is db2, "DatabaseManager must return the exact same instance."
        DatabaseManager.reset_instance()


def test_singleton_thread_safety():
    DatabaseManager.reset_instance()
    instances = []

    def get_instance():
        inst = DatabaseManager(":memory:")
        instances.append(inst)

    threads = [threading.Thread(target=get_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    first = instances[0]
    for inst in instances:
        assert inst is first, "All concurrent threads must receive the identical singleton instance."
    DatabaseManager.reset_instance()


def test_database_manager_schema_initialization():
    DatabaseManager.reset_instance()
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db = DatabaseManager(tmp.name)
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]
        for expected in ["users", "appointments", "medical_records", "invoices", "audit_logs"]:
            assert expected in tables, f"Expected table {expected} to exist in database"
        db.close()
        DatabaseManager.reset_instance()

