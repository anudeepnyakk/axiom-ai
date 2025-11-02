"""
State tracker for Project Axiom.
Tracks file processing status using SQLite database.
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

from .config.models import StateTrackerConfig


class FileStatus(Enum):
    """File processing status states."""
    SEEN = "seen"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StateTracker:
    """Tracks file processing status using SQLite database."""
    
    def __init__(self, config: StateTrackerConfig):
        """Initialize state tracker with configuration."""
        self.config = config
        self.db_path = config.db_path
        self._ensure_db_exists()
        self.conn = self._create_connection()
        self._create_tables()

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        # For in-memory, the db_path is ":memory:"
        # For file-based, it's the actual path.
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def _ensure_db_exists(self) -> None:
        """Ensure database directory exists if not in-memory."""
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Create files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_hash TEXT,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT,
                metadata TEXT
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_path ON files(file_path)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON files(status)
        """)
        
        # Create query_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster session-based lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id ON query_history(session_id)
        """)
        
        self.conn.commit()
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash for file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def record_file_seen(self, file_path: str) -> None:
        """Record that a file has been discovered."""
        file_hash = self._get_file_hash(file_path)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO files 
            (file_path, file_hash, status, updated_at) 
            VALUES (?, ?, ?, ?)
        """, (file_path, file_hash, FileStatus.SEEN.value, datetime.now()))
        self.conn.commit()
    
    def record_processing_start(self, file_path: str) -> None:
        """Record that file processing has started."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE files 
            SET status = ?, updated_at = ? 
            WHERE file_path = ?
        """, (FileStatus.PROCESSING.value, datetime.now(), file_path))
        self.conn.commit()
    
    def record_processing_complete(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record that file processing has completed successfully."""
        import json
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE files 
            SET status = ?, updated_at = ?, metadata = ? 
            WHERE file_path = ?
        """, (FileStatus.COMPLETED.value, datetime.now(), metadata_json, file_path))
        self.conn.commit()
    
    def record_processing_failed(self, file_path: str, error_message: str) -> None:
        """Record that file processing has failed."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE files 
            SET status = ?, updated_at = ?, error_message = ? 
            WHERE file_path = ?
        """, (FileStatus.FAILED.value, datetime.now(), error_message, file_path))
        self.conn.commit()
    
    def get_file_status(self, file_path: str) -> Optional[FileStatus]:
        """Get the current status of a file."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT status FROM files WHERE file_path = ?
        """, (file_path,))
        result = cursor.fetchone()
        
        if result:
            return FileStatus(result[0])
        return None
    
    def get_files_by_status(self, status: FileStatus) -> List[Dict[str, Any]]:
        """Get all files with a specific status."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT file_path, file_hash, status, created_at, updated_at, 
                   error_message, metadata 
            FROM files WHERE status = ?
        """, (status.value,))
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get all files regardless of status."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT file_path, file_hash, status, created_at, updated_at, 
                   error_message, metadata 
            FROM files ORDER BY updated_at DESC
        """)
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_processing_stats(self) -> Dict[str, int]:
        """Get statistics about file processing."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT status, COUNT(*) FROM files GROUP BY status
        """)
        
        stats = {status.value: 0 for status in FileStatus}
        for status, count in cursor.fetchall():
            stats[status] = count
        
        return stats
    
    def cleanup_old_records(self, days: Optional[int] = None) -> int:
        """Remove old records to keep database size manageable."""
        if days is None:
            days = self.config.auto_cleanup_days
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM files 
            WHERE updated_at < ? AND status IN (?, ?)
        """, (cutoff_date, FileStatus.COMPLETED.value, FileStatus.FAILED.value))
        
        deleted_count = cursor.rowcount
        self.conn.commit()
        return deleted_count
    
    # == Query History Methods ==

    def add_query_to_history(self, session_id: str, question: str, answer: str) -> int:
        """
        Adds a question and its answer to the query history for a specific session.

        Args:
            session_id: A unique identifier for the current user session.
            question: The question asked by the user.
            answer: The answer provided by the system.

        Returns:
            The ID of the newly inserted record.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO query_history (session_id, question, answer, created_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, question, answer, datetime.now()))
        self.conn.commit()
        return cursor.lastrowid

    def get_query_history(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves the most recent query history for a specific session.

        Args:
            session_id: The unique identifier for the user session.
            limit: The maximum number of history items to retrieve.

        Returns:
            A list of dictionaries, where each dictionary represents a past Q&A.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT question, answer, created_at
            FROM query_history
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (session_id, limit))
        
        columns = [description[0] for description in cursor.description]
        # We reverse the results so they are in chronological order (oldest first)
        return [dict(zip(columns, row)) for row in reversed(cursor.fetchall())]

    def delete_session(self, session_id: str) -> int:
        """Delete all history rows for a session and return number of deleted items."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            DELETE FROM query_history
            WHERE session_id = ?
            """,
            (session_id,)
        )
        deleted = cursor.rowcount
        self.conn.commit()
        return deleted

    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List past chat sessions with last question and item count."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT q.session_id,
                   q.question AS last_question,
                   q.created_at AS last_at,
                   t.items AS items
            FROM query_history q
            JOIN (
                SELECT session_id, MAX(created_at) AS last_at, COUNT(*) AS items
                FROM query_history
                GROUP BY session_id
            ) t ON t.session_id = q.session_id AND t.last_at = q.created_at
            ORDER BY last_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
