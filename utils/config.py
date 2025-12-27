"""
Configuration Manager Module
Handles application settings with JSON persistence.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any
import threading


@dataclass
class AppConfig:
    """Application configuration settings."""

    # General settings
    app_name: str = "SaadFirewall"
    version: str = "1.0.0"
    language: str = "en"

    # Appearance
    theme: str = "dark"  # dark, light
    font_size: int = 10
    show_tray_icon: bool = True
    minimize_to_tray: bool = True
    start_minimized: bool = False
    start_with_windows: bool = False

    # Network monitoring
    monitor_poll_interval: float = 2.0  # seconds
    monitor_auto_start: bool = True
    show_listening_ports: bool = True
    show_localhost: bool = False

    # Rule engine
    detection_enabled: bool = True
    beaconing_threshold: int = 20
    beaconing_time_window: int = 60
    high_connection_threshold: int = 50
    port_scan_threshold: int = 10
    failed_login_threshold: int = 5

    # Bad ports list
    bad_ports: List[int] = field(default_factory=lambda: [
        4444, 5555, 6666, 6667, 31337, 12345, 27374, 1234, 9001, 8080
    ])

    # Bad IPs list (threat intelligence)
    bad_ips: List[str] = field(default_factory=list)

    # Whitelist
    whitelist_ips: List[str] = field(default_factory=lambda: [
        "127.0.0.1", "0.0.0.0", "::1"
    ])
    whitelist_processes: List[str] = field(default_factory=lambda: [
        "svchost.exe", "System", "System Idle"
    ])

    # Firewall settings
    firewall_auto_block: bool = False
    firewall_block_duration: int = 1800  # 30 minutes in seconds
    firewall_prefix: str = "SaadFirewall_"

    # Logging
    log_directory: str = "logs"
    log_max_size_mb: int = 50
    log_retention_days: int = 30
    log_level: str = "INFO"

    # Event log monitoring
    event_log_enabled: bool = True
    event_log_poll_interval: float = 30.0
    event_log_lookback_minutes: int = 10

    # Alerts
    alert_sound_enabled: bool = True
    alert_notification_enabled: bool = True
    max_alerts_display: int = 100

    # Export/Report
    export_format: str = "txt"  # txt, json, csv
    report_include_charts: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """Create from dictionary."""
        # Filter out unknown keys
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def update(self, **kwargs):
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class ConfigManager:
    """
    Manages application configuration.
    Loads/saves settings from/to JSON file.
    """

    DEFAULT_CONFIG_FILE = "config.json"

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_FILE
        self._config: AppConfig = AppConfig()
        self._lock = threading.Lock()
        self._observers: List[callable] = []

        # Load configuration
        self.load()

    @property
    def config(self) -> AppConfig:
        """Get current configuration."""
        return self._config

    def load(self) -> bool:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config = AppConfig.from_dict(data)
                return True
            else:
                # Create default config file
                self.save()
                return True
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = AppConfig()
            return False

    def save(self) -> bool:
        """Save configuration to file."""
        try:
            with self._lock:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self._config.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return getattr(self._config, key, default)

    def set(self, key: str, value: Any, save: bool = True):
        """Set a configuration value."""
        if hasattr(self._config, key):
            with self._lock:
                setattr(self._config, key, value)
            if save:
                self.save()
            self._notify_observers(key, value)

    def update(self, settings: dict, save: bool = True):
        """Update multiple settings at once."""
        with self._lock:
            for key, value in settings.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
        if save:
            self.save()
        for key, value in settings.items():
            self._notify_observers(key, value)

    def reset(self):
        """Reset to default configuration."""
        self._config = AppConfig()
        self.save()
        self._notify_observers('*', None)

    def add_observer(self, callback: callable):
        """Add observer for configuration changes."""
        if callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(self, callback: callable):
        """Remove observer."""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self, key: str, value: Any):
        """Notify observers of configuration change."""
        for observer in self._observers:
            try:
                observer(key, value)
            except Exception:
                pass

    # Convenience methods for common settings
    def get_theme(self) -> str:
        return self._config.theme

    def set_theme(self, theme: str):
        self.set('theme', theme)

    def get_poll_interval(self) -> float:
        return self._config.monitor_poll_interval

    def set_poll_interval(self, interval: float):
        self.set('monitor_poll_interval', interval)

    def get_bad_ports(self) -> List[int]:
        return self._config.bad_ports.copy()

    def add_bad_port(self, port: int):
        if port not in self._config.bad_ports:
            self._config.bad_ports.append(port)
            self.save()

    def remove_bad_port(self, port: int):
        if port in self._config.bad_ports:
            self._config.bad_ports.remove(port)
            self.save()

    def get_bad_ips(self) -> List[str]:
        return self._config.bad_ips.copy()

    def add_bad_ip(self, ip: str):
        if ip not in self._config.bad_ips:
            self._config.bad_ips.append(ip)
            self.save()

    def remove_bad_ip(self, ip: str):
        if ip in self._config.bad_ips:
            self._config.bad_ips.remove(ip)
            self.save()

    def get_whitelist_ips(self) -> List[str]:
        return self._config.whitelist_ips.copy()

    def add_whitelist_ip(self, ip: str):
        if ip not in self._config.whitelist_ips:
            self._config.whitelist_ips.append(ip)
            self.save()

    def remove_whitelist_ip(self, ip: str):
        if ip in self._config.whitelist_ips:
            self._config.whitelist_ips.remove(ip)
            self.save()

    def get_whitelist_processes(self) -> List[str]:
        return self._config.whitelist_processes.copy()

    def add_whitelist_process(self, process: str):
        if process not in self._config.whitelist_processes:
            self._config.whitelist_processes.append(process)
            self.save()

    def remove_whitelist_process(self, process: str):
        if process in self._config.whitelist_processes:
            self._config.whitelist_processes.remove(process)
            self.save()

    def export_config(self, filepath: str) -> bool:
        """Export configuration to a file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2)
            return True
        except Exception:
            return False

    def import_config(self, filepath: str) -> bool:
        """Import configuration from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._config = AppConfig.from_dict(data)
                self.save()
            return True
        except Exception:
            return False


# Global configuration instance
_config_instance: Optional[ConfigManager] = None


def get_config(config_path: str = None) -> ConfigManager:
    """Get or create the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_path)
    return _config_instance
