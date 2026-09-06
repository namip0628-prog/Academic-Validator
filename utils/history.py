import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent / "records.db"


def init_db():
    """Initializes SQLite tables for activity audit history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            document_name TEXT,
            document_hash TEXT NOT NULL,
            student_name TEXT,
            student_id TEXT,
            institution TEXT,
            course TEXT,
            marks TEXT,
            verdict TEXT NOT NULL,
            tx_hash TEXT,
            block_number INTEGER,
            timestamp INTEGER NOT NULL,
            formatted_date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_audit_entry(
    event_type: str,
    document_name: str,
    document_hash: str,
    student_name: Optional[str] = None,
    student_id: Optional[str] = None,
    institution: Optional[str] = None,
    course: Optional[str] = None,
    marks: Optional[str] = None,
    verdict: str = "AUTHENTIC",
    tx_hash: Optional[str] = None,
    block_number: Optional[int] = None,
) -> int:
    """Adds a registration or verification record to the persistent audit log."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now_ts = int(time.time())
    formatted_date = datetime.fromtimestamp(now_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    cursor.execute("""
        INSERT INTO audit_logs (
            event_type, document_name, document_hash, student_name, student_id,
            institution, course, marks, verdict, tx_hash, block_number,
            timestamp, formatted_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_type,
        document_name or "academic_credential.png",
        document_hash,
        student_name or "-",
        student_id or "-",
        institution or "-",
        course or "-",
        marks or "-",
        verdict,
        tx_hash or "-",
        block_number or 0,
        now_ts,
        formatted_date,
    ))

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_recent_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves the most recent audit activity records."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM audit_logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results


def get_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a specific audit record by its primary key ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM audit_logs WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# Auto-initialize database on import
init_db()
