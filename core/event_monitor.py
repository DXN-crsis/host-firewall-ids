"""
Event Log Monitor Module
Reads Windows Security Event Log for failed login attempts and other security events.
Requires Administrator privileges to access Security logs.
"""

import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import time

# Try to import win32 modules (only available on Windows)
try:
    import win32evtlog
    import win32evtlogutil
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


@dataclass
class SecurityEvent:
    """Represents a Windows Security event."""
    event_id: int
    time_generated: datetime
    source_name: str
    event_type: str
    category: str
    message: str
    computer_name: str
    user_name: str = ""
    source_ip: str = ""
    logon_type: int = 0

    def to_dict(self) -> dict:
        return {
            'event_id': self.event_id,
            'time_generated': self.time_generated.isoformat(),
            'source_name': self.source_name,
            'event_type': self.event_type,
            'category': self.category,
            'message': self.message,
            'computer_name': self.computer_name,
            'user_name': self.user_name,
            'source_ip': self.source_ip,
            'logon_type': self.logon_type
        }


class EventLogWorker(QThread):
    """Background worker for monitoring Windows Event Logs."""

    events_found = pyqtSignal(list)  # List of SecurityEvent
    failed_logins_found = pyqtSignal(list)  # List of failed login events
    error_occurred = pyqtSignal(str)

    # Event IDs of interest
    EVENT_FAILED_LOGIN = 4625  # Failed login attempt
    EVENT_SUCCESSFUL_LOGIN = 4624  # Successful login
    EVENT_ACCOUNT_LOCKOUT = 4740  # Account lockout
    EVENT_LOGOFF = 4634  # Logoff
    EVENT_SPECIAL_LOGON = 4672  # Special privileges assigned

    def __init__(self, poll_interval: float = 30.0, lookback_minutes: int = 10):
        super().__init__()
        self.poll_interval = poll_interval
        self.lookback_minutes = lookback_minutes
        self._running = False
        self._last_check_time = None

    def run(self):
        """Main monitoring loop."""
        if not WIN32_AVAILABLE:
            self.error_occurred.emit("Windows Event Log API not available (pywin32 not installed)")
            return

        self._running = True
        self._last_check_time = datetime.now() - timedelta(minutes=self.lookback_minutes)

        while self._running:
            try:
                # Get failed login events
                failed_logins = self._get_failed_logins()
                if failed_logins:
                    self.failed_logins_found.emit(failed_logins)

                # Update last check time
                self._last_check_time = datetime.now()

            except Exception as e:
                self.error_occurred.emit(f"Event log error: {str(e)}")

            # Sleep for poll interval
            time.sleep(self.poll_interval)

    def stop(self):
        """Stop the monitoring thread."""
        self._running = False
        self.wait()

    def _get_failed_logins(self) -> List[Dict]:
        """Get failed login attempts from Security log."""
        failed_logins = []

        try:
            # Open the Security event log
            handle = win32evtlog.OpenEventLog(None, "Security")

            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

            events = True
            while events:
                events = win32evtlog.ReadEventLog(handle, flags, 0)

                for event in events:
                    # Check if event is recent enough
                    event_time = datetime(
                        event.TimeGenerated.year,
                        event.TimeGenerated.month,
                        event.TimeGenerated.day,
                        event.TimeGenerated.hour,
                        event.TimeGenerated.minute,
                        event.TimeGenerated.second
                    )

                    if event_time < self._last_check_time:
                        # Stop reading, we've gone past our time window
                        events = None
                        break

                    # Check for failed login events
                    # Use bitmask to handle EventID which may have additional flags
                    event_id = event.EventID & 0xFFFF
                    if event_id == self.EVENT_FAILED_LOGIN:
                        login_info = self._parse_failed_login(event)
                        if login_info:
                            failed_logins.append(login_info)

            win32evtlog.CloseEventLog(handle)

        except Exception as e:
            self.error_occurred.emit(f"Failed to read Security log: {str(e)}")

        return failed_logins

    def _parse_failed_login(self, event) -> Optional[Dict]:
        """Parse a failed login event (Event ID 4625)."""
        try:
            # Get event message
            message = win32evtlogutil.SafeFormatMessage(event, "Security")

            # Parse important fields from the message
            info = {
                'event_id': event.EventID & 0xFFFF,
                'time': datetime(
                    event.TimeGenerated.year,
                    event.TimeGenerated.month,
                    event.TimeGenerated.day,
                    event.TimeGenerated.hour,
                    event.TimeGenerated.minute,
                    event.TimeGenerated.second
                ),
                'computer': event.ComputerName,
                'source_ip': '',
                'user_name': '',
                'logon_type': 0,
                'failure_reason': ''
            }

            # Try to extract fields from StringInserts
            if event.StringInserts:
                strings = event.StringInserts
                # Standard positions for 4625 event
                if len(strings) > 5:
                    info['user_name'] = strings[5] if strings[5] else ''
                if len(strings) > 10:
                    info['logon_type'] = int(strings[10]) if strings[10] and strings[10].isdigit() else 0
                if len(strings) > 19:
                    info['source_ip'] = strings[19] if strings[19] and strings[19] != '-' else ''

            return info

        except Exception:
            return None


class EventLogMonitor(QObject):
    """
    Main Event Log Monitor class.
    Monitors Windows Security Event Log for security-related events.
    """

    # Signals forwarded from worker
    events_found = pyqtSignal(list)
    failed_logins_found = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, poll_interval: float = 30.0, lookback_minutes: int = 10):
        super().__init__()
        self.poll_interval = poll_interval
        self.lookback_minutes = lookback_minutes
        self._worker: Optional[EventLogWorker] = None
        self._failed_login_history: List[Dict] = []
        self._available = WIN32_AVAILABLE

    @property
    def is_available(self) -> bool:
        """Check if event log monitoring is available."""
        return self._available

    def start(self):
        """Start event log monitoring."""
        if not self._available:
            self.error_occurred.emit("Event log monitoring requires pywin32 on Windows")
            return

        if self._worker is not None and self._worker.isRunning():
            return

        self._worker = EventLogWorker(self.poll_interval, self.lookback_minutes)

        # Connect worker signals
        self._worker.events_found.connect(self.events_found.emit)
        self._worker.failed_logins_found.connect(self._on_failed_logins)
        self._worker.error_occurred.connect(self.error_occurred.emit)

        self._worker.start()

    def stop(self):
        """Stop event log monitoring."""
        if self._worker is not None:
            self._worker.stop()
            self._worker = None

    def is_running(self) -> bool:
        """Check if monitoring is active."""
        return self._worker is not None and self._worker.isRunning()

    def _on_failed_logins(self, logins: List[Dict]):
        """Handle failed login events."""
        self._failed_login_history.extend(logins)

        # Keep only last 100 events
        if len(self._failed_login_history) > 100:
            self._failed_login_history = self._failed_login_history[-100:]

        self.failed_logins_found.emit(logins)

    def get_failed_login_history(self) -> List[Dict]:
        """Get failed login history."""
        return self._failed_login_history.copy()

    def get_recent_failed_logins(self, minutes: int = 10) -> List[Dict]:
        """Get failed logins from the last N minutes."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [
            login for login in self._failed_login_history
            if login.get('time', datetime.min) > cutoff
        ]


def check_security_log_access() -> bool:
    """
    Check if we have access to read the Security event log.
    This typically requires Administrator privileges.
    """
    if not WIN32_AVAILABLE:
        return False

    try:
        handle = win32evtlog.OpenEventLog(None, "Security")
        win32evtlog.CloseEventLog(handle)
        return True
    except Exception:
        return False


def get_logon_type_description(logon_type: int) -> str:
    """Get human-readable description of logon type."""
    types = {
        2: "Interactive (local keyboard/screen)",
        3: "Network (e.g., file share access)",
        4: "Batch (scheduled task)",
        5: "Service (started by service control manager)",
        7: "Unlock (workstation unlocked)",
        8: "NetworkCleartext (network with cleartext credentials)",
        9: "NewCredentials (cloned token with different credentials)",
        10: "RemoteInteractive (Terminal Services/RDP)",
        11: "CachedInteractive (cached domain credentials)"
    }
    return types.get(logon_type, f"Unknown ({logon_type})")
