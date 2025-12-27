"""
Helper Functions Module
Utility functions for the application.
"""

import os
import sys
import re
import socket
from datetime import datetime
from typing import Optional, Dict, Tuple
import psutil


def is_admin() -> bool:
    """
    Check if the application is running with Administrator privileges.
    Returns True if running as admin on Windows, or as root on Unix.
    """
    try:
        if sys.platform == 'win32':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


def run_as_admin(executable: str = None, args: str = "") -> bool:
    """
    Attempt to restart the application with admin privileges.
    Returns True if successful, False otherwise.
    """
    if sys.platform != 'win32':
        print("Admin elevation only supported on Windows")
        return False

    try:
        import ctypes
        if executable is None:
            executable = sys.executable

        params = ' '.join([sys.argv[0]] + sys.argv[1:])
        if args:
            params += ' ' + args

        # Use ShellExecute with 'runas' verb
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", executable, params, None, 1
        )
        return ret > 32
    except Exception as e:
        print(f"Failed to elevate: {e}")
        return False


def validate_ip(ip: str) -> bool:
    """
    Validate an IP address (IPv4 or IPv6).
    Returns True if valid, False otherwise.
    """
    if not ip:
        return False

    # Handle CIDR notation
    if '/' in ip:
        ip_part, mask = ip.rsplit('/', 1)
        if not mask.isdigit():
            return False
        mask_int = int(mask)
        # Check if it's IPv4 or IPv6 based on presence of ':'
        if ':' in ip_part:
            if not 0 <= mask_int <= 128:
                return False
        else:
            if not 0 <= mask_int <= 32:
                return False
        ip = ip_part

    # Try IPv4
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        pass

    # Try IPv6
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        return True
    except socket.error:
        pass

    return False


def validate_port(port: int) -> bool:
    """
    Validate a port number.
    Returns True if valid (1-65535), False otherwise.
    """
    try:
        port_int = int(port)
        return 1 <= port_int <= 65535
    except (ValueError, TypeError):
        return False


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human-readable string.
    Example: 1536 -> "1.5 KB"
    """
    if bytes_value < 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            if unit == 'B':
                return f"{bytes_value} {unit}"
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024

    return f"{bytes_value:.1f} PB"


def format_timestamp(dt: datetime = None, format_str: str = None) -> str:
    """
    Format a datetime object into a string.
    If dt is None, uses current time.
    """
    if dt is None:
        dt = datetime.now()

    if format_str:
        return dt.strftime(format_str)

    return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_duration(seconds: int) -> str:
    """
    Format seconds into human-readable duration.
    Example: 3665 -> "1h 1m 5s"
    """
    if seconds < 0:
        return "0s"

    parts = []

    hours = seconds // 3600
    if hours:
        parts.append(f"{hours}h")
        seconds %= 3600

    minutes = seconds // 60
    if minutes:
        parts.append(f"{minutes}m")
        seconds %= 60

    if seconds or not parts:
        parts.append(f"{seconds}s")

    return ' '.join(parts)


def get_process_info(pid: int) -> Optional[Dict]:
    """
    Get information about a process by PID.
    Returns dict with name, exe, cmdline, etc.
    """
    try:
        if pid <= 0:
            return {'name': 'System', 'exe': '', 'cmdline': []}

        proc = psutil.Process(pid)
        return {
            'name': proc.name(),
            'exe': proc.exe() if hasattr(proc, 'exe') else '',
            'cmdline': proc.cmdline() if hasattr(proc, 'cmdline') else [],
            'username': proc.username() if hasattr(proc, 'username') else '',
            'create_time': datetime.fromtimestamp(proc.create_time()).isoformat(),
            'status': proc.status(),
            'memory_percent': proc.memory_percent(),
            'cpu_percent': proc.cpu_percent(interval=0.1)
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a filename.
    Removes/replaces invalid characters.
    """
    # Characters not allowed in Windows filenames
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')

    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]

    return sanitized or "unnamed"


def get_local_ips() -> list:
    """
    Get all local IP addresses.
    Returns list of IP strings.
    """
    ips = []
    try:
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ips.append(addr.address)
    except Exception:
        pass
    return ips


def get_hostname() -> str:
    """Get the local hostname."""
    try:
        return socket.gethostname()
    except Exception:
        return "Unknown"


def resolve_ip(ip: str) -> str:
    """
    Attempt to resolve an IP address to a hostname.
    Returns the hostname or the original IP if resolution fails.
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror):
        return ip


def is_private_ip(ip: str) -> bool:
    """
    Check if an IP address is private (RFC 1918).
    """
    try:
        import ipaddress
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except (ValueError, AttributeError):
        # Fallback for basic check
        if ip.startswith('10.'):
            return True
        if ip.startswith('172.'):
            second_octet = int(ip.split('.')[1])
            if 16 <= second_octet <= 31:
                return True
        if ip.startswith('192.168.'):
            return True
        if ip.startswith('127.'):
            return True
        return False


def get_port_service(port: int, protocol: str = 'tcp') -> str:
    """
    Get the service name for a port number.
    Returns service name or "Unknown".
    """
    try:
        return socket.getservbyport(port, protocol)
    except (socket.error, OSError):
        # Common ports not in the system database
        common_ports = {
            80: 'http',
            443: 'https',
            22: 'ssh',
            21: 'ftp',
            25: 'smtp',
            53: 'dns',
            110: 'pop3',
            143: 'imap',
            3306: 'mysql',
            5432: 'postgresql',
            27017: 'mongodb',
            6379: 'redis',
            8080: 'http-proxy',
            3389: 'rdp',
            5900: 'vnc'
        }
        return common_ports.get(port, 'Unknown')


def truncate_string(s: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    Truncate a string to max_length, adding suffix if truncated.
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def parse_ip_range(ip_range: str) -> list:
    """
    Parse an IP range string into a list of IPs.
    Supports: single IP, CIDR notation, range (192.168.1.1-192.168.1.10)
    """
    ips = []

    # Single IP
    if validate_ip(ip_range) and '/' not in ip_range:
        return [ip_range]

    # CIDR notation
    if '/' in ip_range:
        try:
            import ipaddress
            network = ipaddress.ip_network(ip_range, strict=False)
            # Limit to prevent memory issues
            if network.num_addresses > 1000:
                return [str(ip) for ip in list(network.hosts())[:1000]]
            return [str(ip) for ip in network.hosts()]
        except ValueError:
            return []

    # Range notation (e.g., 192.168.1.1-192.168.1.10)
    if '-' in ip_range:
        try:
            import ipaddress
            start_ip, end_ip = ip_range.split('-')
            start = ipaddress.ip_address(start_ip.strip())
            end = ipaddress.ip_address(end_ip.strip())

            current = start
            count = 0
            while current <= end and count < 1000:
                ips.append(str(current))
                current = ipaddress.ip_address(int(current) + 1)
                count += 1
            return ips
        except (ValueError, AttributeError):
            return []

    return []


def get_system_info() -> dict:
    """
    Get basic system information.
    """
    info = {
        'hostname': get_hostname(),
        'platform': sys.platform,
        'python_version': sys.version,
        'local_ips': get_local_ips(),
    }

    try:
        info['cpu_count'] = psutil.cpu_count()
        info['memory_total'] = psutil.virtual_memory().total
        info['memory_available'] = psutil.virtual_memory().available
    except Exception:
        pass

    return info


class RateLimiter:
    """
    Simple rate limiter for tracking action frequencies.
    """

    def __init__(self, max_actions: int, time_window: float):
        """
        Initialize rate limiter.
        max_actions: Maximum number of actions allowed
        time_window: Time window in seconds
        """
        self.max_actions = max_actions
        self.time_window = time_window
        self.actions: Dict[str, list] = {}

    def is_allowed(self, key: str) -> bool:
        """
        Check if an action is allowed for the given key.
        Returns True if allowed, False if rate limited.
        """
        now = datetime.now().timestamp()

        if key not in self.actions:
            self.actions[key] = []

        # Remove old entries
        self.actions[key] = [
            t for t in self.actions[key]
            if now - t < self.time_window
        ]

        # Check if under limit
        if len(self.actions[key]) < self.max_actions:
            self.actions[key].append(now)
            return True

        return False

    def reset(self, key: str = None):
        """Reset rate limiter for a key or all keys."""
        if key:
            self.actions.pop(key, None)
        else:
            self.actions.clear()
