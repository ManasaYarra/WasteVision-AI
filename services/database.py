import os
import sqlite3
import json
import random
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class WasteDatabase:
    """SQLite Database Manager for WasteVision AI classification history, public reports, and impact metrics."""

    def __init__(self, db_path=None):
        if db_path is None:
            data_dir = BASE_DIR / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "waste_history.db"
        
        self.db_path = str(db_path)
        self.init_db()

    def get_connection(self):
        """Create a sqlite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database table schemas."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Household / Individual scan history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    item_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    explanation TEXT,
                    disposal_instructions TEXT,
                    co2_saved_kg REAL DEFAULT 0.0
                )
            """)

            # Public waste overflow reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ref_id TEXT UNIQUE NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    item_name TEXT,
                    category TEXT,
                    confidence REAL,
                    urgency TEXT NOT NULL,
                    priority_rank INTEGER NOT NULL,
                    location TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    notes TEXT,
                    status TEXT DEFAULT 'New'
                )
            """)
            conn.commit()

    def save_classification(self, item_name, category, confidence, explanation, disposal_instructions, co2_saved_kg=0.45):
        """Save a new waste classification record."""
        if isinstance(disposal_instructions, list):
            instructions_str = json.dumps(disposal_instructions)
        else:
            instructions_str = str(disposal_instructions)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO classifications 
                (timestamp, item_name, category, confidence, explanation, disposal_instructions, co2_saved_kg)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, item_name, category, confidence, explanation, instructions_str, co2_saved_kg))
            conn.commit()
            return cursor.lastrowid

    def get_history(self, limit=50):
        """Retrieve recent classification records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, item_name, category, confidence, explanation, disposal_instructions, co2_saved_kg
                FROM classifications
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                item = dict(row)
                try:
                    item["disposal_instructions"] = json.loads(item["disposal_instructions"])
                except Exception:
                    pass
                history.append(item)
            return history

    def get_stats(self):
        """Calculate aggregate impact metrics and category distribution."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as total, SUM(co2_saved_kg) as total_co2 FROM classifications")
            total_row = cursor.fetchone()
            total_items = total_row["total"] if total_row["total"] else 0
            total_co2 = round(total_row["total_co2"], 2) if total_row["total_co2"] else 0.0

            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM classifications 
                GROUP BY category
            """)
            cat_rows = cursor.fetchall()
            
            categories = {
                "Recyclable": 0,
                "Organic": 0,
                "E-waste": 0,
                "Hazardous": 0,
                "General Waste": 0
            }
            for r in cat_rows:
                if r["category"] in categories:
                    categories[r["category"]] = r["count"]

            return {
                "total_items": total_items,
                "total_co2_saved_kg": total_co2,
                "category_counts": categories
            }

    def clear_history(self):
        """Clear all classification history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM classifications")
            conn.commit()

    # --- PUBLIC REPORTS METHODS ---

    def save_public_report(self, item_name, category, confidence, urgency, priority_rank, location, latitude=None, longitude=None, notes=""):
        """Save a new public waste report."""
        ref_id = f"#WV-{random.randint(1000, 9999)}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO public_reports 
                (ref_id, timestamp, item_name, category, confidence, urgency, priority_rank, location, latitude, longitude, notes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'New')
            """, (ref_id, timestamp, item_name, category, confidence, urgency, priority_rank, location, latitude, longitude, notes))
            conn.commit()
            return ref_id

    def get_public_reports(self, status_filter=None, urgency_filter=None):
        """Retrieve public waste reports sorted by priority rank and timestamp."""
        query = "SELECT * FROM public_reports"
        params = []
        conditions = []

        if status_filter and status_filter != "All":
            conditions.append("status = ?")
            params.append(status_filter)
        if urgency_filter and urgency_filter != "All":
            conditions.append("urgency = ?")
            params.append(urgency_filter)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY priority_rank ASC, id DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def update_report_status(self, report_id, new_status):
        """Update report status (New, In Progress, Resolved)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE public_reports 
                SET status = ? 
                WHERE id = ?
            """, (new_status, report_id))
            conn.commit()

    def get_public_reports_stats(self):
        """Return aggregate statistics for Municipal Dashboard."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM public_reports")
            total = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) as high FROM public_reports WHERE urgency LIKE '%High%' AND status != 'Resolved'")
            high_open = cursor.fetchone()["high"]

            cursor.execute("SELECT COUNT(*) as in_prog FROM public_reports WHERE status = 'In Progress'")
            in_progress = cursor.fetchone()["in_prog"]

            cursor.execute("SELECT COUNT(*) as resolved FROM public_reports WHERE status = 'Resolved'")
            resolved = cursor.fetchone()["resolved"]

            return {
                "total": total,
                "high_open": high_open,
                "in_progress": in_progress,
                "resolved": resolved
            }
