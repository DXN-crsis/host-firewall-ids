"""
Logger Module
Centralized logging system with support for:
- Human-readable text logs
- JSONL structured logs for machine processing
- Multiple log levels and filtering
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import threading


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    ALERT = "ALERT"  # Security alerts

    @property
    def numeric(self) -> int:
        levels = {
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
            LogLevel.CRITICAL: 50,
            LogLevel.ALERT: 45
        }
        return levels.get(self, 20)


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    level: str
    category: str
    message: str
    details: Optional[Dict[str, Any]] = None
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    process_name: Optional[str] = None
    rule_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {
            'timestamp': self.timestamp,
            'level': self.level,
            'category': self.category,
            'message': self.message
        }
        if self.details:
            result['details'] = self.details
        if self.source_ip:
            result['source_ip'] = self.source_ip
        if self.dest_ip:
            result['dest_ip'] = self.dest_ip
        if self.process_name:
            result['process_name'] = self.process_name
        if self.rule_id:
            result['rule_id'] = self.rule_id
        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    def to_text(self) -> str:
        """Convert to human-readable text."""
        parts = [
            f"[{self.timestamp}]",
            f"[{self.level}]",
            f"[{self.category}]",
            self.message
        ]
        if self.process_name:
            parts.append(f"(Process: {self.process_name})")
        if self.source_ip:
            parts.append(f"(Source: {self.source_ip})")
        if self.dest_ip:
            parts.append(f"(Dest: {self.dest_ip})")
        return " ".join(parts)


class JSONLHandler(logging.Handler):
    """Custom handler for JSONL (JSON Lines) output."""

    def __init__(self, filename: str, max_size_mb: int = 50):
        super().__init__()
        self.filename = filename
        self.max_size_mb = max_size_mb
        self._lock = threading.Lock()

        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    def emit(self, record: logging.LogRecord):
        """Write a log record to the JSONL file."""
        try:
            with self._lock:
                # Check file size and rotate if needed
                self._check_rotation()

                # Create log entry
                entry = LogEntry(
                    timestamp=datetime.fromtimestamp(record.created).isoformat(),
                    level=record.levelname,
                    category=getattr(record, 'category', 'general'),
                    message=record.getMessage(),
                    details=getattr(record, 'details', None),
                    source_ip=getattr(record, 'source_ip', None),
                    dest_ip=getattr(record, 'dest_ip', None),
                    process_name=getattr(record, 'process_name', None),
                    rule_id=getattr(record, 'rule_id', None)
                )

                # Write to file
                with open(self.filename, 'a', encoding='utf-8') as f:
                    f.write(entry.to_json() + '\n')

        except Exception:
            self.handleError(record)

    def _check_rotation(self):
        """Rotate log file if it exceeds max size."""
        try:
            if os.path.exists(self.filename):
                size_mb = os.path.getsize(self.filename) / (1024 * 1024)
                if size_mb > self.max_size_mb:
                    # Rotate: rename current file with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    base, ext = os.path.splitext(self.filename)
                    rotated_name = f"{base}_{timestamp}{ext}"
                    os.rename(self.filename, rotated_name)
        except Exception:
            pass


class AppLogger:
    """
    Main application logger.
    Provides both human-readable and structured logging.
    """

    def __init__(self, log_dir: str = "logs", app_name: str = "SaadFirewall"):
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self._lock = threading.Lock()
        self._entries: List[LogEntry] = []
        self._max_memory_entries = 1000

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Configure the logging system."""
        # Create logger
        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Text file handler (human-readable)
        text_file = self.log_dir / "app.log"
        text_handler = logging.FileHandler(text_file, encoding='utf-8')
        text_handler.setLevel(logging.INFO)
        text_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(category)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        text_handler.setFormatter(text_format)
        self.logger.addHandler(text_handler)

        # JSONL handler (structured)
        jsonl_file = self.log_dir / "events.jsonl"
        jsonl_handler = JSONLHandler(str(jsonl_file))
        jsonl_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(jsonl_handler)

        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_format = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

    def _log(self, level: LogLevel, category: str, message: str, **kwargs):
        """Internal logging method."""
        # Create LogEntry for memory storage
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            category=category,
            message=message,
            details=kwargs.get('details'),
            source_ip=kwargs.get('source_ip'),
            dest_ip=kwargs.get('dest_ip'),
            process_name=kwargs.get('process_name'),
            rule_id=kwargs.get('rule_id')
        )

        # Store in memory
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max_memory_entries:
                self._entries = self._entries[-self._max_memory_entries:]

        # Log using Python logging
        extra = {
            'category': category,
            'details': kwargs.get('details'),
            'source_ip': kwargs.get('source_ip'),
            'dest_ip': kwargs.get('dest_ip'),
            'process_name': kwargs.get('process_name'),
            'rule_id': kwargs.get('rule_id')
        }

        self.logger.log(level.numeric, message, extra=extra)

    # Public logging methods
    def debug(self, category: str, message: str, **kwargs):
        """Log debug message."""
        self._log(LogLevel.DEBUG, category, message, **kwargs)

    def info(self, category: str, message: str, **kwargs):
        """Log info message."""
        self._log(LogLevel.INFO, category, message, **kwargs)

    def warning(self, category: str, message: str, **kwargs):
        """Log warning message."""
        self._log(LogLevel.WARNING, category, message, **kwargs)

    def error(self, category: str, message: str, **kwargs):
        """Log error message."""
        self._log(LogLevel.ERROR, category, message, **kwargs)

    def critical(self, category: str, message: str, **kwargs):
        """Log critical message."""
        self._log(LogLevel.CRITICAL, category, message, **kwargs)

    def alert(self, category: str, message: str, **kwargs):
        """Log security alert."""
        self._log(LogLevel.ALERT, category, message, **kwargs)

    # Convenience methods for specific categories
    def log_connection(self, message: str, source_ip: str = None,
                       dest_ip: str = None, process_name: str = None, **kwargs):
        """Log network connection event."""
        self.info("connection", message,
                  source_ip=source_ip, dest_ip=dest_ip,
                  process_name=process_name, **kwargs)

    def log_firewall(self, message: str, **kwargs):
        """Log firewall operation."""
        self.info("firewall", message, **kwargs)

    def log_alert(self, message: str, rule_id: str = None, **kwargs):
        """Log security alert."""
        self.alert("security", message, rule_id=rule_id, **kwargs)

    def log_rule_action(self, action: str, rule_id: str, target: str, **kwargs):
        """Log rule engine action."""
        message = f"{action}: {target}"
        self.info("rule_engine", message, rule_id=rule_id, **kwargs)

    # Query methods
    def get_entries(self, limit: int = 100, level: str = None,
                    category: str = None, start_time: datetime = None,
                    end_time: datetime = None) -> List[LogEntry]:
        """Get log entries with optional filtering."""
        with self._lock:
            entries = self._entries.copy()

        # Apply filters
        if level:
            entries = [e for e in entries if e.level == level.upper()]

        if category:
            entries = [e for e in entries if e.category == category]

        if start_time:
            entries = [e for e in entries
                       if datetime.fromisoformat(e.timestamp) >= start_time]

        if end_time:
            entries = [e for e in entries
                       if datetime.fromisoformat(e.timestamp) <= end_time]

        # Return most recent entries
        return entries[-limit:]

    def get_entries_by_ip(self, ip: str, limit: int = 50) -> List[LogEntry]:
        """Get log entries related to a specific IP."""
        with self._lock:
            entries = [
                e for e in self._entries
                if e.source_ip == ip or e.dest_ip == ip
            ]
        return entries[-limit:]

    def get_entries_by_process(self, process_name: str, limit: int = 50) -> List[LogEntry]:
        """Get log entries for a specific process."""
        with self._lock:
            entries = [
                e for e in self._entries
                if e.process_name and process_name.lower() in e.process_name.lower()
            ]
        return entries[-limit:]

    def export_to_file(self, filename: str, format: str = 'txt',
                       entries: List[LogEntry] = None) -> bool:
        """Export log entries to a file."""
        try:
            if entries is None:
                entries = self.get_entries(limit=10000)

            with open(filename, 'w', encoding='utf-8') as f:
                if format == 'json':
                    json.dump([e.to_dict() for e in entries], f, indent=2)
                elif format == 'jsonl':
                    for entry in entries:
                        f.write(entry.to_json() + '\n')
                elif format == 'csv':
                    import csv
                    if entries:
                        writer = csv.DictWriter(f, fieldnames=entries[0].to_dict().keys())
                        writer.writeheader()
                        for entry in entries:
                            writer.writerow(entry.to_dict())
                else:  # txt
                    for entry in entries:
                        f.write(entry.to_text() + '\n')

            return True
        except Exception as e:
            self.error("logger", f"Failed to export logs: {str(e)}")
            return False

    def generate_report(self, filename: str, start_time: datetime = None,
                        end_time: datetime = None) -> bool:
        """Generate a summary report."""
        try:
            entries = self.get_entries(limit=10000, start_time=start_time, end_time=end_time)

            # Calculate statistics
            stats = {
                'total_entries': len(entries),
                'by_level': {},
                'by_category': {},
                'unique_ips': set(),
                'unique_processes': set()
            }

            for entry in entries:
                # Count by level
                stats['by_level'][entry.level] = stats['by_level'].get(entry.level, 0) + 1

                # Count by category
                stats['by_category'][entry.category] = stats['by_category'].get(entry.category, 0) + 1

                # Track unique IPs
                if entry.source_ip:
                    stats['unique_ips'].add(entry.source_ip)
                if entry.dest_ip:
                    stats['unique_ips'].add(entry.dest_ip)

                # Track processes
                if entry.process_name:
                    stats['unique_processes'].add(entry.process_name)

            # Generate report
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("SaadFirewall - Security Report\n")
                f.write("=" * 60 + "\n\n")

                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if start_time:
                    f.write(f"Period Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                if end_time:
                    f.write(f"Period End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")

                f.write("-" * 40 + "\n")
                f.write("SUMMARY\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total Events: {stats['total_entries']}\n")
                f.write(f"Unique IPs: {len(stats['unique_ips'])}\n")
                f.write(f"Unique Processes: {len(stats['unique_processes'])}\n\n")

                f.write("-" * 40 + "\n")
                f.write("EVENTS BY SEVERITY\n")
                f.write("-" * 40 + "\n")
                for level, count in sorted(stats['by_level'].items()):
                    f.write(f"  {level}: {count}\n")
                f.write("\n")

                f.write("-" * 40 + "\n")
                f.write("EVENTS BY CATEGORY\n")
                f.write("-" * 40 + "\n")
                for category, count in sorted(stats['by_category'].items()):
                    f.write(f"  {category}: {count}\n")
                f.write("\n")

                f.write("-" * 40 + "\n")
                f.write("RECENT ALERTS (Last 20)\n")
                f.write("-" * 40 + "\n")
                alerts = [e for e in entries if e.level == 'ALERT'][-20:]
                for alert in alerts:
                    f.write(f"  [{alert.timestamp}] {alert.message}\n")
                f.write("\n")

                f.write("=" * 60 + "\n")
                f.write("End of Report\n")
                f.write("=" * 60 + "\n")

            return True
        except Exception as e:
            self.error("logger", f"Failed to generate report: {str(e)}")
            return False

    def clear_memory_logs(self):
        """Clear in-memory log entries."""
        with self._lock:
            self._entries.clear()


# Global logger instance
_logger_instance: Optional[AppLogger] = None


def get_logger(log_dir: str = "logs") -> AppLogger:
    """Get or create the global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AppLogger(log_dir=log_dir)
    return _logger_instance
