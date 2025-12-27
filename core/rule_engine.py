"""
Rule Engine Module
Implements intrusion detection rules to identify suspicious network activity.
Analyzes connection patterns and generates security alerts.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Callable
from enum import Enum
from collections import defaultdict
import threading
from PyQt6.QtCore import QObject, pyqtSignal
import json


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def color(self) -> str:
        """Get color for this severity level."""
        colors = {
            AlertSeverity.LOW: "#4CAF50",      # Green
            AlertSeverity.MEDIUM: "#FF9800",   # Orange
            AlertSeverity.HIGH: "#f44336",     # Red
            AlertSeverity.CRITICAL: "#9C27B0"  # Purple
        }
        return colors.get(self, "#757575")

    @property
    def priority(self) -> int:
        """Get numeric priority (higher = more severe)."""
        priorities = {
            AlertSeverity.LOW: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.HIGH: 3,
            AlertSeverity.CRITICAL: 4
        }
        return priorities.get(self, 0)


@dataclass
class Alert:
    """Represents a security alert."""
    id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    source_ip: str = ""
    source_port: int = 0
    dest_ip: str = ""
    dest_port: int = 0
    process_name: str = ""
    pid: int = 0
    recommended_action: str = ""
    is_acknowledged: bool = False
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'source_ip': self.source_ip,
            'source_port': self.source_port,
            'dest_ip': self.dest_ip,
            'dest_port': self.dest_port,
            'process_name': self.process_name,
            'pid': self.pid,
            'recommended_action': self.recommended_action,
            'is_acknowledged': self.is_acknowledged,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Alert':
        """Create from dictionary."""
        data['severity'] = AlertSeverity(data['severity'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class DetectionRule:
    """Defines a detection rule configuration."""
    id: str
    name: str
    description: str
    enabled: bool = True
    severity: AlertSeverity = AlertSeverity.MEDIUM
    threshold: int = 10
    time_window: int = 60  # seconds
    cooldown: int = 300  # seconds before triggering again
    parameters: dict = field(default_factory=dict)


class RuleEngine(QObject):
    """
    Main Rule Engine for intrusion detection.
    Analyzes connection data and generates alerts based on configured rules.
    """

    # Signals
    alert_generated = pyqtSignal(object)  # Alert object
    rule_triggered = pyqtSignal(str, str)  # rule_id, message

    def __init__(self):
        super().__init__()
        self._rules: Dict[str, DetectionRule] = {}
        self._alerts: List[Alert] = []
        self._alert_counter = 0
        self._lock = threading.Lock()

        # Tracking data for rules
        self._ip_connection_times: Dict[str, List[datetime]] = defaultdict(list)
        self._connection_counts: Dict[str, int] = defaultdict(int)
        self._last_alert_time: Dict[str, datetime] = {}
        self._unique_ips_per_process: Dict[str, Set[str]] = defaultdict(set)

        # Initialize default rules
        self._init_default_rules()

        # Configurable bad ports list
        self.bad_ports: Set[int] = {
            4444,   # Metasploit default
            5555,   # Android Debug Bridge
            6666,   # IRC (potentially malicious)
            6667,   # IRC
            31337,  # Back Orifice
            12345,  # NetBus
            27374,  # SubSeven
            1234,   # Common malware port
            9001,   # Tor default
            8080,   # Common proxy/malware
        }

        # Known bad IPs (user-configurable threat list)
        self.bad_ips: Set[str] = set()

        # Whitelist for excluded IPs
        self.whitelist_ips: Set[str] = {
            "127.0.0.1",
            "0.0.0.0",
            "::1",
        }

        # Whitelist for excluded processes
        self.whitelist_processes: Set[str] = {
            "svchost.exe",
            "System",
            "System Idle",
        }

    def _init_default_rules(self):
        """Initialize default detection rules."""
        default_rules = [
            DetectionRule(
                id="R001",
                name="Beaconing Detection",
                description="Detects when a process connects to many unique IPs in a short time (possible malware beaconing)",
                severity=AlertSeverity.HIGH,
                threshold=20,
                time_window=60,
                cooldown=300
            ),
            DetectionRule(
                id="R002",
                name="Suspicious Port Access",
                description="Detects connections to known suspicious ports commonly used by malware",
                severity=AlertSeverity.MEDIUM,
                threshold=1,
                time_window=0,
                cooldown=60
            ),
            DetectionRule(
                id="R003",
                name="High Connection Rate",
                description="Detects excessive new connections from a single process",
                severity=AlertSeverity.MEDIUM,
                threshold=50,
                time_window=60,
                cooldown=120
            ),
            DetectionRule(
                id="R004",
                name="Failed Login Attempts",
                description="Detects repeated failed login attempts from Windows Event Log",
                severity=AlertSeverity.HIGH,
                threshold=5,
                time_window=600,
                cooldown=300
            ),
            DetectionRule(
                id="R005",
                name="Known Bad IP",
                description="Detects connections to IPs in the threat intelligence list",
                severity=AlertSeverity.CRITICAL,
                threshold=1,
                time_window=0,
                cooldown=60
            ),
            DetectionRule(
                id="R006",
                name="Port Scan Detection",
                description="Detects when a remote IP probes multiple ports in short time",
                severity=AlertSeverity.HIGH,
                threshold=10,
                time_window=30,
                cooldown=300
            ),
        ]

        for rule in default_rules:
            self._rules[rule.id] = rule

    def analyze_connections(self, connections: list):
        """
        Analyze a list of connections for suspicious activity.
        This is the main entry point called by the network monitor.
        """
        now = datetime.now()

        # Group connections by process
        process_connections: Dict[str, list] = defaultdict(list)
        for conn in connections:
            if hasattr(conn, 'process_name'):
                process_connections[conn.process_name].append(conn)

        # Run each enabled rule
        for rule in self._rules.values():
            if not rule.enabled:
                continue

            # Check cooldown
            last_alert = self._last_alert_time.get(rule.id)
            if last_alert and (now - last_alert).total_seconds() < rule.cooldown:
                continue

            # Run rule-specific detection
            if rule.id == "R001":
                self._check_beaconing(connections, process_connections, rule, now)
            elif rule.id == "R002":
                self._check_bad_ports(connections, rule, now)
            elif rule.id == "R003":
                self._check_high_connection_rate(connections, process_connections, rule, now)
            elif rule.id == "R005":
                self._check_bad_ips(connections, rule, now)
            elif rule.id == "R006":
                self._check_port_scan(connections, rule, now)

        # Cleanup old tracking data
        self._cleanup_old_data(now)

    def _check_beaconing(self, connections: list, process_conns: dict,
                         rule: DetectionRule, now: datetime):
        """Check for beaconing behavior (many unique IPs from one process)."""
        for process_name, conns in process_conns.items():
            if process_name in self.whitelist_processes:
                continue

            unique_ips = set()
            for conn in conns:
                if hasattr(conn, 'remote_ip') and conn.remote_ip and conn.remote_ip != "*":
                    if conn.remote_ip not in self.whitelist_ips:
                        unique_ips.add(conn.remote_ip)

            # Track unique IPs over time window
            cache_key = f"beacon_{process_name}"
            self._unique_ips_per_process[cache_key].update(unique_ips)

            if len(self._unique_ips_per_process[cache_key]) >= rule.threshold:
                alert = self._create_alert(
                    rule=rule,
                    title=f"Possible Beaconing Detected: {process_name}",
                    description=f"Process '{process_name}' connected to {len(self._unique_ips_per_process[cache_key])} unique IPs in a short time. This may indicate malware beaconing or C2 communication.",
                    process_name=process_name,
                    recommended_action=f"Investigate process '{process_name}' and consider blocking if suspicious.",
                    metadata={'unique_ip_count': len(self._unique_ips_per_process[cache_key])}
                )
                self._emit_alert(alert, rule.id)
                self._unique_ips_per_process[cache_key].clear()

    def _check_bad_ports(self, connections: list, rule: DetectionRule, now: datetime):
        """Check for connections to known bad ports."""
        for conn in connections:
            remote_port = getattr(conn, 'remote_port', 0)
            if remote_port in self.bad_ports:
                remote_ip = getattr(conn, 'remote_ip', '')
                if remote_ip in self.whitelist_ips:
                    continue

                process_name = getattr(conn, 'process_name', 'Unknown')

                # Use unique key for cooldown
                cooldown_key = f"{rule.id}_{remote_ip}_{remote_port}"
                last_alert = self._last_alert_time.get(cooldown_key)
                if last_alert and (now - last_alert).total_seconds() < rule.cooldown:
                    continue

                alert = self._create_alert(
                    rule=rule,
                    title=f"Suspicious Port Connection: {remote_port}",
                    description=f"Process '{process_name}' connected to port {remote_port} which is commonly used by malware.",
                    source_ip=getattr(conn, 'local_ip', ''),
                    source_port=getattr(conn, 'local_port', 0),
                    dest_ip=remote_ip,
                    dest_port=remote_port,
                    process_name=process_name,
                    pid=getattr(conn, 'pid', 0),
                    recommended_action=f"Block port {remote_port} and investigate the process."
                )
                self._emit_alert(alert, cooldown_key)

    def _check_high_connection_rate(self, connections: list, process_conns: dict,
                                    rule: DetectionRule, now: datetime):
        """Check for excessive connection rates."""
        for process_name, conns in process_conns.items():
            if process_name in self.whitelist_processes:
                continue

            # Count established connections
            active_count = sum(1 for c in conns
                             if getattr(c, 'status', '') == 'ESTABLISHED')

            if active_count >= rule.threshold:
                cooldown_key = f"{rule.id}_{process_name}"
                last_alert = self._last_alert_time.get(cooldown_key)
                if last_alert and (now - last_alert).total_seconds() < rule.cooldown:
                    continue

                alert = self._create_alert(
                    rule=rule,
                    title=f"High Connection Rate: {process_name}",
                    description=f"Process '{process_name}' has {active_count} active connections, which exceeds the threshold of {rule.threshold}.",
                    process_name=process_name,
                    recommended_action="Monitor this process for unusual activity.",
                    metadata={'connection_count': active_count}
                )
                self._emit_alert(alert, cooldown_key)

    def _check_bad_ips(self, connections: list, rule: DetectionRule, now: datetime):
        """Check for connections to known bad IPs."""
        if not self.bad_ips:
            return

        for conn in connections:
            remote_ip = getattr(conn, 'remote_ip', '')
            if remote_ip in self.bad_ips:
                process_name = getattr(conn, 'process_name', 'Unknown')

                cooldown_key = f"{rule.id}_{remote_ip}"
                last_alert = self._last_alert_time.get(cooldown_key)
                if last_alert and (now - last_alert).total_seconds() < rule.cooldown:
                    continue

                alert = self._create_alert(
                    rule=rule,
                    title=f"Connection to Known Bad IP: {remote_ip}",
                    description=f"Process '{process_name}' connected to IP {remote_ip} which is in the threat intelligence list.",
                    source_ip=getattr(conn, 'local_ip', ''),
                    source_port=getattr(conn, 'local_port', 0),
                    dest_ip=remote_ip,
                    dest_port=getattr(conn, 'remote_port', 0),
                    process_name=process_name,
                    pid=getattr(conn, 'pid', 0),
                    recommended_action=f"IMMEDIATELY block IP {remote_ip} and investigate the process!"
                )
                self._emit_alert(alert, cooldown_key)

    def _check_port_scan(self, connections: list, rule: DetectionRule, now: datetime):
        """Detect port scanning behavior (one IP connecting to many ports)."""
        ip_ports: Dict[str, Set[int]] = defaultdict(set)

        for conn in connections:
            remote_ip = getattr(conn, 'remote_ip', '')
            local_port = getattr(conn, 'local_port', 0)

            if remote_ip and remote_ip not in self.whitelist_ips:
                ip_ports[remote_ip].add(local_port)

        for ip, ports in ip_ports.items():
            if len(ports) >= rule.threshold:
                cooldown_key = f"{rule.id}_{ip}"
                last_alert = self._last_alert_time.get(cooldown_key)
                if last_alert and (now - last_alert).total_seconds() < rule.cooldown:
                    continue

                alert = self._create_alert(
                    rule=rule,
                    title=f"Possible Port Scan from {ip}",
                    description=f"IP {ip} connected to {len(ports)} different ports, indicating possible port scanning.",
                    source_ip=ip,
                    recommended_action=f"Block IP {ip} to prevent further scanning.",
                    metadata={'scanned_ports': list(ports)[:20]}  # Limit to first 20
                )
                self._emit_alert(alert, cooldown_key)

    def check_failed_logins(self, failed_attempts: List[dict]):
        """
        Check for failed login attempts from Event Log.
        Called by EventLogMonitor.
        """
        rule = self._rules.get("R004")
        if not rule or not rule.enabled:
            return

        now = datetime.now()
        cooldown_key = rule.id

        last_alert = self._last_alert_time.get(cooldown_key)
        if last_alert and (now - last_alert).total_seconds() < rule.cooldown:
            return

        if len(failed_attempts) >= rule.threshold:
            # Group by source IP if available
            source_ips = set()
            for attempt in failed_attempts:
                if 'source_ip' in attempt:
                    source_ips.add(attempt['source_ip'])

            alert = self._create_alert(
                rule=rule,
                title=f"Multiple Failed Login Attempts Detected",
                description=f"Detected {len(failed_attempts)} failed login attempts in the last {rule.time_window // 60} minutes. Source IPs: {', '.join(source_ips) if source_ips else 'Local'}",
                recommended_action="Review Windows Security Event Log and consider blocking source IPs.",
                metadata={
                    'attempt_count': len(failed_attempts),
                    'source_ips': list(source_ips)
                }
            )
            self._emit_alert(alert, cooldown_key)

    def _create_alert(self, rule: DetectionRule, title: str, description: str,
                      source_ip: str = "", source_port: int = 0,
                      dest_ip: str = "", dest_port: int = 0,
                      process_name: str = "", pid: int = 0,
                      recommended_action: str = "",
                      metadata: dict = None) -> Alert:
        """Create a new alert."""
        with self._lock:
            self._alert_counter += 1
            alert_id = f"ALERT-{self._alert_counter:06d}"

        return Alert(
            id=alert_id,
            rule_id=rule.id,
            rule_name=rule.name,
            severity=rule.severity,
            title=title,
            description=description,
            timestamp=datetime.now(),
            source_ip=source_ip,
            source_port=source_port,
            dest_ip=dest_ip,
            dest_port=dest_port,
            process_name=process_name,
            pid=pid,
            recommended_action=recommended_action,
            metadata=metadata or {}
        )

    def _emit_alert(self, alert: Alert, cooldown_key: str):
        """Emit alert and update cooldown."""
        self._last_alert_time[cooldown_key] = datetime.now()
        self._alerts.append(alert)
        self.alert_generated.emit(alert)
        self.rule_triggered.emit(alert.rule_id, alert.title)

    def _cleanup_old_data(self, now: datetime):
        """Clean up old tracking data to prevent memory leaks."""
        cutoff = now - timedelta(minutes=10)

        # Clean IP connection times
        for ip in list(self._ip_connection_times.keys()):
            self._ip_connection_times[ip] = [
                t for t in self._ip_connection_times[ip]
                if t > cutoff
            ]
            if not self._ip_connection_times[ip]:
                del self._ip_connection_times[ip]

    # Rule management methods
    def get_rules(self) -> List[DetectionRule]:
        """Get all detection rules."""
        return list(self._rules.values())

    def get_rule(self, rule_id: str) -> Optional[DetectionRule]:
        """Get a specific rule by ID."""
        return self._rules.get(rule_id)

    def update_rule(self, rule_id: str, **kwargs):
        """Update a rule's parameters."""
        if rule_id in self._rules:
            rule = self._rules[rule_id]
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)

    def enable_rule(self, rule_id: str, enabled: bool = True):
        """Enable or disable a rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = enabled

    def get_alerts(self, limit: int = 100) -> List[Alert]:
        """Get recent alerts."""
        return self._alerts[-limit:]

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get a specific alert by ID."""
        for alert in self._alerts:
            if alert.id == alert_id:
                return alert
        return None

    def acknowledge_alert(self, alert_id: str):
        """Mark an alert as acknowledged."""
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.is_acknowledged = True
                break

    def clear_alerts(self):
        """Clear all alerts."""
        self._alerts.clear()

    def add_bad_ip(self, ip: str):
        """Add an IP to the bad IP list."""
        self.bad_ips.add(ip)

    def remove_bad_ip(self, ip: str):
        """Remove an IP from the bad IP list."""
        self.bad_ips.discard(ip)

    def add_bad_port(self, port: int):
        """Add a port to the bad ports list."""
        self.bad_ports.add(port)

    def remove_bad_port(self, port: int):
        """Remove a port from the bad ports list."""
        self.bad_ports.discard(port)

    def add_whitelist_ip(self, ip: str):
        """Add an IP to the whitelist."""
        self.whitelist_ips.add(ip)

    def remove_whitelist_ip(self, ip: str):
        """Remove an IP from the whitelist."""
        self.whitelist_ips.discard(ip)

    def export_config(self) -> dict:
        """Export rule engine configuration."""
        return {
            'rules': {r.id: {
                'enabled': r.enabled,
                'threshold': r.threshold,
                'time_window': r.time_window,
                'cooldown': r.cooldown,
                'severity': r.severity.value
            } for r in self._rules.values()},
            'bad_ports': list(self.bad_ports),
            'bad_ips': list(self.bad_ips),
            'whitelist_ips': list(self.whitelist_ips),
            'whitelist_processes': list(self.whitelist_processes)
        }

    def import_config(self, config: dict):
        """Import rule engine configuration."""
        if 'rules' in config:
            for rule_id, settings in config['rules'].items():
                if rule_id in self._rules:
                    rule = self._rules[rule_id]
                    rule.enabled = settings.get('enabled', True)
                    rule.threshold = settings.get('threshold', rule.threshold)
                    rule.time_window = settings.get('time_window', rule.time_window)
                    rule.cooldown = settings.get('cooldown', rule.cooldown)
                    if 'severity' in settings:
                        rule.severity = AlertSeverity(settings['severity'])

        if 'bad_ports' in config:
            self.bad_ports = set(config['bad_ports'])
        if 'bad_ips' in config:
            self.bad_ips = set(config['bad_ips'])
        if 'whitelist_ips' in config:
            self.whitelist_ips = set(config['whitelist_ips'])
        if 'whitelist_processes' in config:
            self.whitelist_processes = set(config['whitelist_processes'])
