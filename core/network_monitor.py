"""
Network Monitor Module
Monitors active network connections using psutil.
Maps PIDs to process names and provides real-time connection data.
"""

import psutil
import socket
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QMutex
import time


@dataclass
class ConnectionInfo:
    """Represents a single network connection."""
    local_ip: str
    local_port: int
    remote_ip: str
    remote_port: int
    protocol: str  # TCP or UDP
    status: str
    pid: int
    process_name: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'local_ip': self.local_ip,
            'local_port': self.local_port,
            'remote_ip': self.remote_ip,
            'remote_port': self.remote_port,
            'protocol': self.protocol,
            'status': self.status,
            'pid': self.pid,
            'process_name': self.process_name,
            'timestamp': self.timestamp.isoformat()
        }

    @property
    def unique_key(self) -> str:
        """Unique identifier for this connection."""
        return f"{self.local_ip}:{self.local_port}-{self.remote_ip}:{self.remote_port}-{self.protocol}"


class NetworkMonitorWorker(QThread):
    """
    Background worker thread for network monitoring.
    Polls connections at regular intervals and emits signals with data.
    """

    # Signals
    connections_updated = pyqtSignal(list)  # List of ConnectionInfo
    stats_updated = pyqtSignal(dict)  # Statistics dictionary
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self, poll_interval: float = 2.0):
        super().__init__()
        self.poll_interval = poll_interval
        self._running = False
        self._mutex = QMutex()
        self._process_cache: Dict[int, str] = {}
        self._cache_timestamp = 0
        self._cache_ttl = 5  # Refresh process cache every 5 seconds

    def run(self):
        """Main monitoring loop."""
        self._running = True

        while self._running:
            try:
                connections = self._get_connections()
                stats = self._calculate_stats(connections)

                # Emit signals
                self.connections_updated.emit(connections)
                self.stats_updated.emit(stats)

            except Exception as e:
                self.error_occurred.emit(f"Monitoring error: {str(e)}")

            # Sleep for poll interval
            time.sleep(self.poll_interval)

    def stop(self):
        """Stop the monitoring thread."""
        self._running = False
        self.wait()

    def _get_process_name(self, pid: int) -> str:
        """Get process name from PID with caching."""
        current_time = time.time()

        # Refresh cache if expired
        if current_time - self._cache_timestamp > self._cache_ttl:
            self._process_cache.clear()
            self._cache_timestamp = current_time

        # Check cache first
        if pid in self._process_cache:
            return self._process_cache[pid]

        # Try to get process name
        try:
            if pid == 0:
                name = "System Idle"
            else:
                proc = psutil.Process(pid)
                name = proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            name = "Unknown"

        self._process_cache[pid] = name
        return name

    def _get_connections(self) -> List[ConnectionInfo]:
        """Get all active network connections."""
        connections = []

        # Get TCP connections
        try:
            for conn in psutil.net_connections(kind='tcp'):
                if conn.status == 'NONE':
                    continue

                local_ip = conn.laddr.ip if conn.laddr else ""
                local_port = conn.laddr.port if conn.laddr else 0
                remote_ip = conn.raddr.ip if conn.raddr else ""
                remote_port = conn.raddr.port if conn.raddr else 0

                # Skip listening sockets without remote address for cleaner display
                if not remote_ip and conn.status == 'LISTEN':
                    remote_ip = "*"
                    remote_port = 0

                conn_info = ConnectionInfo(
                    local_ip=local_ip,
                    local_port=local_port,
                    remote_ip=remote_ip,
                    remote_port=remote_port,
                    protocol="TCP",
                    status=conn.status,
                    pid=conn.pid or 0,
                    process_name=self._get_process_name(conn.pid or 0)
                )
                connections.append(conn_info)
        except (psutil.AccessDenied, PermissionError):
            pass

        # Get UDP connections
        try:
            for conn in psutil.net_connections(kind='udp'):
                local_ip = conn.laddr.ip if conn.laddr else ""
                local_port = conn.laddr.port if conn.laddr else 0
                remote_ip = conn.raddr.ip if conn.raddr else "*"
                remote_port = conn.raddr.port if conn.raddr else 0

                conn_info = ConnectionInfo(
                    local_ip=local_ip,
                    local_port=local_port,
                    remote_ip=remote_ip,
                    remote_port=remote_port,
                    protocol="UDP",
                    status="ACTIVE",
                    pid=conn.pid or 0,
                    process_name=self._get_process_name(conn.pid or 0)
                )
                connections.append(conn_info)
        except (psutil.AccessDenied, PermissionError):
            pass

        return connections

    def _calculate_stats(self, connections: List[ConnectionInfo]) -> dict:
        """Calculate statistics from connections."""
        stats = {
            'total_connections': len(connections),
            'tcp_count': 0,
            'udp_count': 0,
            'established_count': 0,
            'listening_count': 0,
            'top_remote_ips': {},
            'top_ports': {},
            'top_processes': {},
            'unique_remote_ips': set()
        }

        for conn in connections:
            # Protocol counts
            if conn.protocol == "TCP":
                stats['tcp_count'] += 1
            else:
                stats['udp_count'] += 1

            # Status counts
            if conn.status == "ESTABLISHED":
                stats['established_count'] += 1
            elif conn.status == "LISTEN":
                stats['listening_count'] += 1

            # Track remote IPs
            if conn.remote_ip and conn.remote_ip != "*":
                stats['unique_remote_ips'].add(conn.remote_ip)
                stats['top_remote_ips'][conn.remote_ip] = \
                    stats['top_remote_ips'].get(conn.remote_ip, 0) + 1

            # Track ports
            if conn.remote_port:
                stats['top_ports'][conn.remote_port] = \
                    stats['top_ports'].get(conn.remote_port, 0) + 1

            # Track processes
            if conn.process_name and conn.process_name != "Unknown":
                stats['top_processes'][conn.process_name] = \
                    stats['top_processes'].get(conn.process_name, 0) + 1

        # Sort and limit top items
        stats['top_remote_ips'] = dict(
            sorted(stats['top_remote_ips'].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        stats['top_ports'] = dict(
            sorted(stats['top_ports'].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        stats['top_processes'] = dict(
            sorted(stats['top_processes'].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        stats['unique_remote_ips'] = len(stats['unique_remote_ips'])

        return stats


class NetworkMonitor(QObject):
    """
    Main Network Monitor class.
    Manages the background monitoring thread and provides interface for UI.
    """

    # Signals forwarded from worker
    connections_updated = pyqtSignal(list)
    stats_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, poll_interval: float = 2.0):
        super().__init__()
        self.poll_interval = poll_interval
        self._worker: Optional[NetworkMonitorWorker] = None
        self._connection_history: List[ConnectionInfo] = []
        self._history_limit = 1000

    def start(self):
        """Start network monitoring."""
        if self._worker is not None and self._worker.isRunning():
            return

        self._worker = NetworkMonitorWorker(self.poll_interval)

        # Connect worker signals
        self._worker.connections_updated.connect(self._on_connections_updated)
        self._worker.stats_updated.connect(self.stats_updated.emit)
        self._worker.error_occurred.connect(self.error_occurred.emit)

        self._worker.start()

    def stop(self):
        """Stop network monitoring."""
        if self._worker is not None:
            self._worker.stop()
            self._worker = None

    def is_running(self) -> bool:
        """Check if monitoring is active."""
        return self._worker is not None and self._worker.isRunning()

    def set_poll_interval(self, interval: float):
        """Update poll interval (requires restart)."""
        self.poll_interval = interval
        if self._worker:
            self._worker.poll_interval = interval

    def _on_connections_updated(self, connections: List[ConnectionInfo]):
        """Handle new connections from worker."""
        # Update history
        self._connection_history.extend(connections)

        # Trim history if needed
        if len(self._connection_history) > self._history_limit:
            self._connection_history = self._connection_history[-self._history_limit:]

        # Forward signal
        self.connections_updated.emit(connections)

    def get_connection_history(self) -> List[ConnectionInfo]:
        """Get connection history."""
        return self._connection_history.copy()

    def get_snapshot(self) -> List[ConnectionInfo]:
        """Get current connection snapshot (blocking call)."""
        worker = NetworkMonitorWorker()
        return worker._get_connections()


def get_local_ip() -> str:
    """Get the local machine's primary IP address."""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def get_network_interfaces() -> Dict[str, List[str]]:
    """Get all network interfaces and their IP addresses."""
    interfaces = {}
    for iface, addrs in psutil.net_if_addrs().items():
        ips = []
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ips.append(addr.address)
        if ips:
            interfaces[iface] = ips
    return interfaces
