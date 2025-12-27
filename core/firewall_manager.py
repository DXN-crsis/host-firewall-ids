"""
Firewall Manager Module
Manages Windows Firewall rules via PowerShell commands.
Creates, deletes, enables, and disables firewall rules with a unique prefix.
"""

import subprocess
import re
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal
import threading


# Unique prefix for all rules created by this application
RULE_PREFIX = "SaadFirewall_"


class RuleDirection(Enum):
    """Firewall rule direction."""
    INBOUND = "Inbound"
    OUTBOUND = "Outbound"
    BOTH = "Both"


class RuleAction(Enum):
    """Firewall rule action."""
    BLOCK = "Block"
    ALLOW = "Allow"


class RuleProtocol(Enum):
    """Network protocol."""
    TCP = "TCP"
    UDP = "UDP"
    ANY = "Any"


@dataclass
class FirewallRule:
    """Represents a Windows Firewall rule."""
    name: str
    display_name: str
    direction: RuleDirection
    action: RuleAction
    enabled: bool
    protocol: RuleProtocol = RuleProtocol.ANY
    local_port: Optional[int] = None
    remote_port: Optional[int] = None
    remote_address: Optional[str] = None
    local_address: Optional[str] = None
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'direction': self.direction.value,
            'action': self.action.value,
            'enabled': self.enabled,
            'protocol': self.protocol.value,
            'local_port': self.local_port,
            'remote_port': self.remote_port,
            'remote_address': self.remote_address,
            'local_address': self.local_address,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FirewallRule':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            display_name=data['display_name'],
            direction=RuleDirection(data['direction']),
            action=RuleAction(data['action']),
            enabled=data['enabled'],
            protocol=RuleProtocol(data.get('protocol', 'Any')),
            local_port=data.get('local_port'),
            remote_port=data.get('remote_port'),
            remote_address=data.get('remote_address'),
            local_address=data.get('local_address'),
            description=data.get('description', ''),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now()
        )


class FirewallManager(QObject):
    """
    Manages Windows Firewall rules using PowerShell.
    All operations require Administrator privileges.
    """

    # Signals
    rule_created = pyqtSignal(object)  # FirewallRule
    rule_deleted = pyqtSignal(str)  # rule name
    rule_updated = pyqtSignal(str, bool)  # rule name, enabled
    operation_completed = pyqtSignal(bool, str)  # success, message
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self._rules_cache: List[FirewallRule] = []
        self._last_cache_update = None

    @staticmethod
    def is_admin() -> bool:
        """Check if the application is running with Administrator privileges."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def _run_powershell(self, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Execute a PowerShell command.
        Returns (success, output/error).
        """
        try:
            # Construct full PowerShell command
            full_command = [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command", command
            ]

            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except FileNotFoundError:
            return False, "PowerShell not found"
        except Exception as e:
            return False, str(e)

    def _generate_rule_name(self, rule_type: str, value: str, direction: RuleDirection = None) -> str:
        """Generate a unique rule name with our prefix."""
        name = f"{RULE_PREFIX}{rule_type}_{value}"
        if direction and direction != RuleDirection.BOTH:
            name += f"_{direction.value[:3]}"
        return name

    def block_ip(self, ip: str, direction: RuleDirection = RuleDirection.BOTH,
                 description: str = "") -> Tuple[bool, str]:
        """
        Block an IP address (inbound and/or outbound).
        Returns (success, message).
        """
        if not self._validate_ip(ip):
            return False, f"Invalid IP address: {ip}"

        results = []

        if direction in (RuleDirection.INBOUND, RuleDirection.BOTH):
            rule_name = self._generate_rule_name("Block_IP", ip, RuleDirection.INBOUND)
            cmd = f'''
            New-NetFirewallRule -DisplayName "{rule_name}" `
                -Direction Inbound `
                -Action Block `
                -RemoteAddress "{ip}" `
                -Description "{description or 'Blocked by SaadFirewall'}"
            '''
            success, msg = self._run_powershell(cmd)
            results.append(("Inbound", success, msg))

            if success:
                rule = FirewallRule(
                    name=rule_name,
                    display_name=rule_name,
                    direction=RuleDirection.INBOUND,
                    action=RuleAction.BLOCK,
                    enabled=True,
                    remote_address=ip,
                    description=description
                )
                self.rule_created.emit(rule)

        if direction in (RuleDirection.OUTBOUND, RuleDirection.BOTH):
            rule_name = self._generate_rule_name("Block_IP", ip, RuleDirection.OUTBOUND)
            cmd = f'''
            New-NetFirewallRule -DisplayName "{rule_name}" `
                -Direction Outbound `
                -Action Block `
                -RemoteAddress "{ip}" `
                -Description "{description or 'Blocked by SaadFirewall'}"
            '''
            success, msg = self._run_powershell(cmd)
            results.append(("Outbound", success, msg))

            if success:
                rule = FirewallRule(
                    name=rule_name,
                    display_name=rule_name,
                    direction=RuleDirection.OUTBOUND,
                    action=RuleAction.BLOCK,
                    enabled=True,
                    remote_address=ip,
                    description=description
                )
                self.rule_created.emit(rule)

        # Summarize results
        success_count = sum(1 for _, s, _ in results if s)
        if success_count == len(results):
            return True, f"Successfully blocked IP {ip}"
        elif success_count > 0:
            return True, f"Partially blocked IP {ip} (some directions failed)"
        else:
            return False, f"Failed to block IP {ip}: {results[0][2] if results else 'Unknown error'}"

    def unblock_ip(self, ip: str) -> Tuple[bool, str]:
        """Remove all blocking rules for an IP address."""
        if not self._validate_ip(ip):
            return False, f"Invalid IP address: {ip}"

        # Find and remove all rules for this IP
        patterns = [
            self._generate_rule_name("Block_IP", ip, RuleDirection.INBOUND),
            self._generate_rule_name("Block_IP", ip, RuleDirection.OUTBOUND),
        ]

        removed = 0
        for pattern in patterns:
            cmd = f'Remove-NetFirewallRule -DisplayName "{pattern}" -ErrorAction SilentlyContinue'
            success, _ = self._run_powershell(cmd)
            if success:
                removed += 1
                self.rule_deleted.emit(pattern)

        if removed > 0:
            return True, f"Successfully unblocked IP {ip}"
        else:
            return False, f"No blocking rules found for IP {ip}"

    def block_port(self, port: int, protocol: RuleProtocol = RuleProtocol.TCP,
                   direction: RuleDirection = RuleDirection.INBOUND,
                   description: str = "") -> Tuple[bool, str]:
        """Block a specific port."""
        if not 1 <= port <= 65535:
            return False, f"Invalid port number: {port}"

        rule_name = self._generate_rule_name("Block_Port", f"{port}_{protocol.value}", direction)

        protocol_str = protocol.value if protocol != RuleProtocol.ANY else "TCP,UDP"
        direction_str = direction.value if direction != RuleDirection.BOTH else "Inbound"

        cmd = f'''
        New-NetFirewallRule -DisplayName "{rule_name}" `
            -Direction {direction_str} `
            -Action Block `
            -LocalPort {port} `
            -Protocol {protocol_str} `
            -Description "{description or 'Blocked by SaadFirewall'}"
        '''

        success, msg = self._run_powershell(cmd)

        if success:
            rule = FirewallRule(
                name=rule_name,
                display_name=rule_name,
                direction=direction,
                action=RuleAction.BLOCK,
                enabled=True,
                protocol=protocol,
                local_port=port,
                description=description
            )
            self.rule_created.emit(rule)
            return True, f"Successfully blocked port {port}/{protocol.value}"
        else:
            return False, f"Failed to block port {port}: {msg}"

    def unblock_port(self, port: int, protocol: RuleProtocol = RuleProtocol.TCP) -> Tuple[bool, str]:
        """Remove blocking rule for a port."""
        # Try to find and remove the rule
        patterns = [
            self._generate_rule_name("Block_Port", f"{port}_{protocol.value}", RuleDirection.INBOUND),
            self._generate_rule_name("Block_Port", f"{port}_{protocol.value}", RuleDirection.OUTBOUND),
        ]

        removed = 0
        for pattern in patterns:
            cmd = f'Remove-NetFirewallRule -DisplayName "{pattern}" -ErrorAction SilentlyContinue'
            success, _ = self._run_powershell(cmd)
            if success:
                removed += 1
                self.rule_deleted.emit(pattern)

        if removed > 0:
            return True, f"Successfully unblocked port {port}"
        else:
            return False, f"No blocking rules found for port {port}"

    def enable_rule(self, rule_name: str) -> Tuple[bool, str]:
        """Enable a firewall rule."""
        cmd = f'Enable-NetFirewallRule -DisplayName "{rule_name}"'
        success, msg = self._run_powershell(cmd)

        if success:
            self.rule_updated.emit(rule_name, True)
            return True, f"Successfully enabled rule: {rule_name}"
        else:
            return False, f"Failed to enable rule: {msg}"

    def disable_rule(self, rule_name: str) -> Tuple[bool, str]:
        """Disable a firewall rule."""
        cmd = f'Disable-NetFirewallRule -DisplayName "{rule_name}"'
        success, msg = self._run_powershell(cmd)

        if success:
            self.rule_updated.emit(rule_name, False)
            return True, f"Successfully disabled rule: {rule_name}"
        else:
            return False, f"Failed to disable rule: {msg}"

    def delete_rule(self, rule_name: str) -> Tuple[bool, str]:
        """Delete a firewall rule."""
        cmd = f'Remove-NetFirewallRule -DisplayName "{rule_name}"'
        success, msg = self._run_powershell(cmd)

        if success:
            self.rule_deleted.emit(rule_name)
            return True, f"Successfully deleted rule: {rule_name}"
        else:
            return False, f"Failed to delete rule: {msg}"

    def get_our_rules(self) -> List[FirewallRule]:
        """Get all firewall rules created by this application."""
        cmd = f'''
        Get-NetFirewallRule -DisplayName "{RULE_PREFIX}*" |
        Select-Object Name, DisplayName, Direction, Action, Enabled |
        ConvertTo-Json -Compress
        '''

        success, output = self._run_powershell(cmd)

        if not success or not output:
            return []

        try:
            # Parse JSON output
            data = json.loads(output)

            # Handle single result vs array
            if isinstance(data, dict):
                data = [data]

            rules = []
            for item in data:
                # Get additional address/port filter info
                address_info = self._get_rule_address_filter(item.get('Name', ''))

                rule = FirewallRule(
                    name=item.get('Name', ''),
                    display_name=item.get('DisplayName', ''),
                    direction=RuleDirection(item.get('Direction', 'Inbound').replace('1', 'Inbound').replace('2', 'Outbound')),
                    action=RuleAction(item.get('Action', 'Block').replace('2', 'Block').replace('4', 'Allow')),
                    enabled=item.get('Enabled', 'True') in (True, 'True', '1', 1),
                    remote_address=address_info.get('remote_address'),
                    local_port=address_info.get('local_port')
                )
                rules.append(rule)

            self._rules_cache = rules
            self._last_cache_update = datetime.now()
            return rules

        except json.JSONDecodeError:
            return []

    def _get_rule_address_filter(self, rule_name: str) -> dict:
        """Get address and port filter info for a rule."""
        result = {'remote_address': None, 'local_port': None}

        # Get address filter
        cmd = f'''
        Get-NetFirewallRule -Name "{rule_name}" |
        Get-NetFirewallAddressFilter |
        Select-Object RemoteAddress |
        ConvertTo-Json -Compress
        '''

        success, output = self._run_powershell(cmd)
        if success and output:
            try:
                data = json.loads(output)
                if isinstance(data, dict):
                    addr = data.get('RemoteAddress', 'Any')
                    if addr and addr != 'Any':
                        result['remote_address'] = addr
            except json.JSONDecodeError:
                pass

        # Get port filter
        cmd = f'''
        Get-NetFirewallRule -Name "{rule_name}" |
        Get-NetFirewallPortFilter |
        Select-Object LocalPort |
        ConvertTo-Json -Compress
        '''

        success, output = self._run_powershell(cmd)
        if success and output:
            try:
                data = json.loads(output)
                if isinstance(data, dict):
                    port = data.get('LocalPort', 'Any')
                    if port and port != 'Any':
                        try:
                            result['local_port'] = int(port)
                        except (ValueError, TypeError):
                            pass
            except json.JSONDecodeError:
                pass

        return result

    def get_firewall_status(self) -> dict:
        """Get current Windows Firewall status."""
        cmd = '''
        Get-NetFirewallProfile |
        Select-Object Name, Enabled |
        ConvertTo-Json -Compress
        '''

        success, output = self._run_powershell(cmd)

        if not success or not output:
            return {}

        try:
            data = json.loads(output)
            if isinstance(data, dict):
                data = [data]

            status = {}
            for profile in data:
                name = profile.get('Name', 'Unknown')
                enabled = profile.get('Enabled', False)
                status[name] = enabled in (True, 'True', '1', 1)

            return status

        except json.JSONDecodeError:
            return {}

    def cleanup_all_rules(self) -> Tuple[bool, str]:
        """Remove all rules created by this application."""
        cmd = f'Remove-NetFirewallRule -DisplayName "{RULE_PREFIX}*" -ErrorAction SilentlyContinue'
        success, msg = self._run_powershell(cmd)

        if success:
            self._rules_cache.clear()
            return True, "All SaadFirewall rules have been removed"
        else:
            return False, f"Failed to cleanup rules: {msg}"

    @staticmethod
    def _validate_ip(ip: str) -> bool:
        """Validate an IP address format."""
        # IPv4 pattern
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(p) <= 255 for p in parts)

        # IPv6 basic check (simplified)
        if ':' in ip:
            return True

        # CIDR notation
        if '/' in ip:
            base_ip, mask = ip.rsplit('/', 1)
            return FirewallManager._validate_ip(base_ip) and mask.isdigit()

        return False

    def get_rule_count(self) -> int:
        """Get the count of our firewall rules."""
        cmd = f'(Get-NetFirewallRule -DisplayName "{RULE_PREFIX}*" -ErrorAction SilentlyContinue | Measure-Object).Count'
        success, output = self._run_powershell(cmd)

        if success and output:
            try:
                return int(output.strip())
            except ValueError:
                pass
        return 0

    def export_rules(self) -> List[dict]:
        """Export all our rules as a list of dictionaries."""
        rules = self.get_our_rules()
        return [rule.to_dict() for rule in rules]

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is currently blocked by our rules."""
        for rule in self._rules_cache:
            if rule.remote_address == ip and rule.action == RuleAction.BLOCK and rule.enabled:
                return True
        return False


# PowerShell command templates for reference
POWERSHELL_TEMPLATES = """
# Block IP (Inbound)
New-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_{IP}_In" -Direction Inbound -Action Block -RemoteAddress "{IP}"

# Block IP (Outbound)
New-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_{IP}_Out" -Direction Outbound -Action Block -RemoteAddress "{IP}"

# Block Port (TCP)
New-NetFirewallRule -DisplayName "SaadFirewall_Block_Port_{PORT}_TCP_In" -Direction Inbound -Action Block -LocalPort {PORT} -Protocol TCP

# List our rules
Get-NetFirewallRule -DisplayName "SaadFirewall_*"

# Remove a rule
Remove-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_{IP}"

# Enable/Disable rule
Enable-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_{IP}"
Disable-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_{IP}"

# Get firewall profiles status
Get-NetFirewallProfile | Select-Object Name, Enabled

# Remove all our rules
Remove-NetFirewallRule -DisplayName "SaadFirewall_*"
"""
