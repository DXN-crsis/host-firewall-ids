"""
Database Module
SQLite database for storing alerts, connection history, and statistics.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
import threading
from pathlib import Path


class DatabaseManager:
    """
    Manages SQLite database operations.
    Uses WAL mode for better concurrent access.
    """

    def __init__(self, db_path: str = "data/alerts.db"):
        self.db_path = db_path
        self._lock = threading.Lock()

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @contextmanager
    def _transaction(self):
        """Context manager for database transactions."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema."""
        with self._transaction() as conn:
            # Alerts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    rule_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    timestamp TEXT NOT NULL,
                    source_ip TEXT,
                    source_port INTEGER,
                    dest_ip TEXT,
                    dest_port INTEGER,
                    process_name TEXT,
                    pid INTEGER,
                    recommended_action TEXT,
                    is_acknowledged INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Connection history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS connection_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    local_ip TEXT,
                    local_port INTEGER,
                    remote_ip TEXT,
                    remote_port INTEGER,
                    protocol TEXT,
                    status TEXT,
                    pid INTEGER,
                    process_name TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Blocked IPs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS blocked_ips (
                    ip TEXT PRIMARY KEY,
                    reason TEXT,
                    blocked_at TEXT NOT NULL,
                    expires_at TEXT,
                    is_permanent INTEGER DEFAULT 0,
                    created_by TEXT
                )
            ''')

            # Firewall rules history
            conn.execute('''
                CREATE TABLE IF NOT EXISTS firewall_rules_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')

            # Statistics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_date TEXT NOT NULL,
                    total_connections INTEGER DEFAULT 0,
                    unique_ips INTEGER DEFAULT 0,
                    alerts_count INTEGER DEFAULT 0,
                    blocked_count INTEGER DEFAULT 0,
                    data TEXT
                )
            ''')

            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_source_ip ON alerts(source_ip)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_connection_history_timestamp ON connection_history(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_connection_history_remote_ip ON connection_history(remote_ip)')

    # Alert operations
    def save_alert(self, alert: dict) -> bool:
        """Save an alert to the database."""
        try:
            with self._transaction() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO alerts
                    (id, rule_id, rule_name, severity, title, description, timestamp,
                     source_ip, source_port, dest_ip, dest_port, process_name, pid,
                     recommended_action, is_acknowledged, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.get('id'),
                    alert.get('rule_id'),
                    alert.get('rule_name'),
                    alert.get('severity'),
                    alert.get('title'),
                    alert.get('description'),
                    alert.get('timestamp'),
                    alert.get('source_ip'),
                    alert.get('source_port'),
                    alert.get('dest_ip'),
                    alert.get('dest_port'),
                    alert.get('process_name'),
                    alert.get('pid'),
                    alert.get('recommended_action'),
                    1 if alert.get('is_acknowledged') else 0,
                    json.dumps(alert.get('metadata', {}))
                ))
            return True
        except Exception as e:
            print(f"Error saving alert: {e}")
            return False

    def get_alerts(self, limit: int = 100, offset: int = 0,
                   severity: str = None, start_time: str = None,
                   end_time: str = None, acknowledged: bool = None) -> List[dict]:
        """Get alerts with optional filtering."""
        try:
            with self._transaction() as conn:
                query = "SELECT * FROM alerts WHERE 1=1"
                params = []

                if severity:
                    query += " AND severity = ?"
                    params.append(severity)

                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time)

                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time)

                if acknowledged is not None:
                    query += " AND is_acknowledged = ?"
                    params.append(1 if acknowledged else 0)

                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor = conn.execute(query, params)
                rows = cursor.fetchall()

                alerts = []
                for row in rows:
                    alert = dict(row)
                    alert['metadata'] = json.loads(alert.get('metadata', '{}'))
                    alert['is_acknowledged'] = bool(alert.get('is_acknowledged'))
                    alerts.append(alert)

                return alerts
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged."""
        try:
            with self._transaction() as conn:
                conn.execute(
                    "UPDATE alerts SET is_acknowledged = 1 WHERE id = ?",
                    (alert_id,)
                )
            return True
        except Exception:
            return False

    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert."""
        try:
            with self._transaction() as conn:
                conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
            return True
        except Exception:
            return False

    def get_alert_count(self, severity: str = None) -> int:
        """Get total alert count."""
        try:
            with self._transaction() as conn:
                if severity:
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM alerts WHERE severity = ?",
                        (severity,)
                    )
                else:
                    cursor = conn.execute("SELECT COUNT(*) FROM alerts")
                return cursor.fetchone()[0]
        except Exception:
            return 0

    # Connection history operations
    def save_connections(self, connections: List[dict]) -> bool:
        """Save connection snapshots to history."""
        try:
            with self._transaction() as conn:
                for c in connections:
                    conn.execute('''
                        INSERT INTO connection_history
                        (local_ip, local_port, remote_ip, remote_port, protocol,
                         status, pid, process_name, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        c.get('local_ip'),
                        c.get('local_port'),
                        c.get('remote_ip'),
                        c.get('remote_port'),
                        c.get('protocol'),
                        c.get('status'),
                        c.get('pid'),
                        c.get('process_name'),
                        c.get('timestamp', datetime.now().isoformat())
                    ))
            return True
        except Exception as e:
            print(f"Error saving connections: {e}")
            return False

    def get_connection_history(self, limit: int = 100, remote_ip: str = None,
                               process_name: str = None) -> List[dict]:
        """Get connection history with optional filtering."""
        try:
            with self._transaction() as conn:
                query = "SELECT * FROM connection_history WHERE 1=1"
                params = []

                if remote_ip:
                    query += " AND remote_ip = ?"
                    params.append(remote_ip)

                if process_name:
                    query += " AND process_name LIKE ?"
                    params.append(f"%{process_name}%")

                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)

                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []

    def cleanup_old_connections(self, days: int = 7) -> int:
        """Delete connection history older than specified days."""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            with self._transaction() as conn:
                cursor = conn.execute(
                    "DELETE FROM connection_history WHERE timestamp < ?",
                    (cutoff,)
                )
                return cursor.rowcount
        except Exception:
            return 0

    # Blocked IPs operations
    def add_blocked_ip(self, ip: str, reason: str = "", expires_at: str = None,
                       is_permanent: bool = False, created_by: str = "user") -> bool:
        """Add an IP to the blocked list."""
        try:
            with self._transaction() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO blocked_ips
                    (ip, reason, blocked_at, expires_at, is_permanent, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    ip, reason, datetime.now().isoformat(),
                    expires_at, 1 if is_permanent else 0, created_by
                ))
            return True
        except Exception:
            return False

    def remove_blocked_ip(self, ip: str) -> bool:
        """Remove an IP from the blocked list."""
        try:
            with self._transaction() as conn:
                conn.execute("DELETE FROM blocked_ips WHERE ip = ?", (ip,))
            return True
        except Exception:
            return False

    def get_blocked_ips(self) -> List[dict]:
        """Get all blocked IPs."""
        try:
            with self._transaction() as conn:
                cursor = conn.execute("SELECT * FROM blocked_ips")
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is in the blocked list."""
        try:
            with self._transaction() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM blocked_ips WHERE ip = ?", (ip,)
                )
                return cursor.fetchone() is not None
        except Exception:
            return False

    def cleanup_expired_blocks(self) -> int:
        """Remove expired temporary blocks."""
        try:
            now = datetime.now().isoformat()
            with self._transaction() as conn:
                cursor = conn.execute('''
                    DELETE FROM blocked_ips
                    WHERE is_permanent = 0 AND expires_at IS NOT NULL AND expires_at < ?
                ''', (now,))
                return cursor.rowcount
        except Exception:
            return 0

    # Firewall rules history
    def log_firewall_action(self, rule_name: str, action: str, details: str = "") -> bool:
        """Log a firewall action."""
        try:
            with self._transaction() as conn:
                conn.execute('''
                    INSERT INTO firewall_rules_history (rule_name, action, details, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (rule_name, action, details, datetime.now().isoformat()))
            return True
        except Exception:
            return False

    def get_firewall_history(self, limit: int = 100) -> List[dict]:
        """Get firewall actions history."""
        try:
            with self._transaction() as conn:
                cursor = conn.execute('''
                    SELECT * FROM firewall_rules_history
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []

    # Statistics
    def save_daily_stats(self, stats: dict) -> bool:
        """Save daily statistics."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            with self._transaction() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO statistics
                    (stat_date, total_connections, unique_ips, alerts_count, blocked_count, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    today,
                    stats.get('total_connections', 0),
                    stats.get('unique_ips', 0),
                    stats.get('alerts_count', 0),
                    stats.get('blocked_count', 0),
                    json.dumps(stats)
                ))
            return True
        except Exception:
            return False

    def get_statistics(self, days: int = 30) -> List[dict]:
        """Get statistics for the last N days."""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            with self._transaction() as conn:
                cursor = conn.execute('''
                    SELECT * FROM statistics
                    WHERE stat_date >= ?
                    ORDER BY stat_date DESC
                ''', (cutoff,))
                stats = []
                for row in cursor.fetchall():
                    stat = dict(row)
                    stat['data'] = json.loads(stat.get('data', '{}'))
                    stats.append(stat)
                return stats
        except Exception:
            return []

    # Utility methods
    def get_db_size(self) -> int:
        """Get database file size in bytes."""
        try:
            return os.path.getsize(self.db_path)
        except Exception:
            return 0

    def vacuum(self):
        """Optimize database by vacuuming."""
        try:
            conn = self._get_connection()
            conn.execute("VACUUM")
            conn.close()
        except Exception:
            pass

    def export_data(self, filepath: str) -> bool:
        """Export all data to a JSON file."""
        try:
            data = {
                'alerts': self.get_alerts(limit=10000),
                'blocked_ips': self.get_blocked_ips(),
                'firewall_history': self.get_firewall_history(limit=1000),
                'statistics': self.get_statistics(days=365),
                'exported_at': datetime.now().isoformat()
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
