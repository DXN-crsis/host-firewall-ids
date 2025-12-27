#!/usr/bin/env python3
"""
SaadFirewall - Smart Host Firewall + Intrusion Detection System
Main application entry point.

A defensive security tool for Windows that provides:
- Real-time network connection monitoring
- Rule-based intrusion detection
- Windows Firewall integration
- Comprehensive logging and alerting

Author: Graduation Project Team
License: Educational Use
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

# Import application modules
from core.network_monitor import NetworkMonitor
from core.rule_engine import RuleEngine
from core.firewall_manager import FirewallManager
from core.event_monitor import EventLogMonitor
from utils.config import ConfigManager, get_config
from utils.logger import AppLogger, get_logger
from utils.database import DatabaseManager
from utils.helpers import is_admin
from ui.main_window import MainWindow
from ui.styles import apply_theme


class SaadFirewallApp:
    """
    Main application class that coordinates all components.
    """

    def __init__(self):
        # Initialize Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("SaadFirewall")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("SaadFirewall")

        # Set default font
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)

        # Initialize components
        self._init_config()
        self._init_logger()
        self._init_database()
        self._init_core_components()
        self._init_ui()

        # Connect signals
        self._connect_signals()

        # Check admin status
        self._check_admin_status()

    def _init_config(self):
        """Initialize configuration manager."""
        config_path = PROJECT_ROOT / "config.json"
        self.config_manager = ConfigManager(str(config_path))
        self.config = self.config_manager.config

    def _init_logger(self):
        """Initialize logging system."""
        log_dir = PROJECT_ROOT / self.config.log_directory
        self.logger = AppLogger(str(log_dir))
        self.logger.info("system", "SaadFirewall starting...")

    def _init_database(self):
        """Initialize database."""
        db_path = PROJECT_ROOT / "data" / "alerts.db"
        self.database = DatabaseManager(str(db_path))

    def _init_core_components(self):
        """Initialize core monitoring and detection components."""
        # Network monitor
        self.network_monitor = NetworkMonitor(
            poll_interval=self.config.monitor_poll_interval
        )

        # Rule engine
        self.rule_engine = RuleEngine()

        # Apply rule settings from config
        self._apply_rule_settings()

        # Firewall manager
        self.firewall_manager = FirewallManager()

        # Event log monitor
        self.event_monitor = EventLogMonitor(
            poll_interval=self.config.event_log_poll_interval,
            lookback_minutes=self.config.event_log_lookback_minutes
        )

    def _apply_rule_settings(self):
        """Apply rule settings from configuration."""
        # Set bad ports
        self.rule_engine.bad_ports = set(self.config.bad_ports)

        # Set bad IPs
        self.rule_engine.bad_ips = set(self.config.bad_ips)

        # Set whitelists
        self.rule_engine.whitelist_ips = set(self.config.whitelist_ips)
        self.rule_engine.whitelist_processes = set(self.config.whitelist_processes)

        # Update rule thresholds
        self.rule_engine.update_rule("R001", threshold=self.config.beaconing_threshold)
        self.rule_engine.update_rule("R003", threshold=self.config.high_connection_threshold)
        self.rule_engine.update_rule("R004", threshold=self.config.failed_login_threshold)
        self.rule_engine.update_rule("R006", threshold=self.config.port_scan_threshold)

    def _init_ui(self):
        """Initialize the user interface."""
        # Apply theme
        apply_theme(self.app, self.config.theme)

        # Create main window
        self.main_window = MainWindow(self.config)

        # Load settings into UI
        self.main_window.load_settings(self.config)

    def _connect_signals(self):
        """Connect all signals between components."""
        # Network monitor signals
        self.network_monitor.connections_updated.connect(self._on_connections_updated)
        self.network_monitor.stats_updated.connect(self._on_stats_updated)
        self.network_monitor.error_occurred.connect(self._on_monitor_error)

        # Rule engine signals
        self.rule_engine.alert_generated.connect(self._on_alert_generated)

        # Event monitor signals
        self.event_monitor.failed_logins_found.connect(self._on_failed_logins)
        self.event_monitor.error_occurred.connect(self._on_event_monitor_error)

        # Firewall manager signals
        self.firewall_manager.rule_created.connect(self._on_rule_created)
        self.firewall_manager.rule_deleted.connect(self._on_rule_deleted)
        self.firewall_manager.error_occurred.connect(self._on_firewall_error)

        # Main window signals
        self.main_window.start_monitoring.connect(self._start_monitoring)
        self.main_window.stop_monitoring.connect(self._stop_monitoring)
        self.main_window.block_ip.connect(self._block_ip)
        self.main_window.block_port.connect(self._block_port)
        self.main_window.delete_rule.connect(self._delete_rule)
        self.main_window.toggle_rule.connect(self._toggle_rule)
        self.main_window.cleanup_rules.connect(self._cleanup_rules)
        self.main_window.refresh_rules.connect(self._refresh_rules)
        self.main_window.save_settings.connect(self._save_settings)
        self.main_window.export_logs.connect(self._export_logs)
        self.main_window.generate_report.connect(self._generate_report)

    def _check_admin_status(self):
        """Check and display admin status."""
        admin_status = is_admin()
        self.main_window.set_admin_status(admin_status)

        if not admin_status:
            self.logger.warning("system", "Running without administrator privileges")
            # Show warning on first run
            QTimer.singleShot(500, self.main_window.show_admin_required_dialog)

    def _start_monitoring(self):
        """Start all monitoring services."""
        self.logger.info("system", "Starting monitoring services...")

        # Start network monitor
        self.network_monitor.start()

        # Start event log monitor if enabled
        if self.config.event_log_enabled and self.event_monitor.is_available:
            self.event_monitor.start()

        self.main_window.set_monitoring_state(True)
        self.main_window.show_status_message("Monitoring started")
        self.logger.info("system", "Monitoring services started")

    def _stop_monitoring(self):
        """Stop all monitoring services."""
        self.logger.info("system", "Stopping monitoring services...")

        self.network_monitor.stop()
        self.event_monitor.stop()

        self.main_window.set_monitoring_state(False)
        self.main_window.show_status_message("Monitoring stopped")
        self.logger.info("system", "Monitoring services stopped")

    def _on_connections_updated(self, connections: list):
        """Handle new connection data from monitor."""
        # Update UI
        self.main_window.update_connections(connections)

        # Analyze connections for threats
        if self.config.detection_enabled:
            self.rule_engine.analyze_connections(connections)

    def _on_stats_updated(self, stats: dict):
        """Handle statistics update."""
        self.main_window.update_stats(stats)

    def _on_alert_generated(self, alert):
        """Handle new security alert."""
        # Log the alert
        self.logger.log_alert(
            alert.title,
            rule_id=alert.rule_id,
            source_ip=alert.source_ip,
            dest_ip=alert.dest_ip,
            process_name=alert.process_name
        )

        # Save to database
        self.database.save_alert(alert.to_dict())

        # Update UI
        self.main_window.add_alert(alert)

        # Auto-block if enabled
        if self.config.firewall_auto_block:
            target_ip = alert.source_ip or alert.dest_ip
            if target_ip and target_ip not in self.rule_engine.whitelist_ips:
                self._block_ip(target_ip, "Both", f"Auto-blocked: {alert.title}")

    def _on_failed_logins(self, logins: list):
        """Handle failed login events from Windows Event Log."""
        self.rule_engine.check_failed_logins(logins)

    def _on_monitor_error(self, error: str):
        """Handle network monitor error."""
        self.logger.error("monitor", error)

    def _on_event_monitor_error(self, error: str):
        """Handle event monitor error."""
        self.logger.warning("event_monitor", error)

    def _on_firewall_error(self, error: str):
        """Handle firewall manager error."""
        self.logger.error("firewall", error)
        self.main_window.show_error("Firewall Error", error)

    def _on_rule_created(self, rule):
        """Handle firewall rule creation."""
        self.logger.log_firewall(f"Rule created: {rule.display_name}")
        self.database.log_firewall_action(rule.display_name, "created")
        self._refresh_rules()
        self.main_window.show_status_message(f"Rule created: {rule.display_name}")

    def _on_rule_deleted(self, rule_name: str):
        """Handle firewall rule deletion."""
        self.logger.log_firewall(f"Rule deleted: {rule_name}")
        self.database.log_firewall_action(rule_name, "deleted")
        self._refresh_rules()
        self.main_window.show_status_message(f"Rule deleted: {rule_name}")

    def _block_ip(self, ip: str, direction: str, reason: str):
        """Block an IP address."""
        if not is_admin():
            self.main_window.show_error(
                "Admin Required",
                "Blocking IPs requires administrator privileges."
            )
            return

        self.logger.info("firewall", f"Blocking IP: {ip} ({direction})")

        # Determine direction
        from core.firewall_manager import RuleDirection
        dir_map = {
            "Both": RuleDirection.BOTH,
            "Inbound": RuleDirection.INBOUND,
            "Outbound": RuleDirection.OUTBOUND
        }
        direction_enum = dir_map.get(direction, RuleDirection.BOTH)

        success, message = self.firewall_manager.block_ip(ip, direction_enum, reason)

        if success:
            self.database.add_blocked_ip(ip, reason)
            self.rule_engine.add_bad_ip(ip)
            self.main_window.show_status_message(message)
        else:
            self.main_window.show_error("Block Failed", message)

    def _block_port(self, port: int, protocol: str, direction: str, reason: str):
        """Block a port."""
        if not is_admin():
            self.main_window.show_error(
                "Admin Required",
                "Blocking ports requires administrator privileges."
            )
            return

        self.logger.info("firewall", f"Blocking port: {port}/{protocol} ({direction})")

        from core.firewall_manager import RuleDirection, RuleProtocol
        dir_map = {"Inbound": RuleDirection.INBOUND, "Outbound": RuleDirection.OUTBOUND}
        proto_map = {"TCP": RuleProtocol.TCP, "UDP": RuleProtocol.UDP}

        success, message = self.firewall_manager.block_port(
            port,
            proto_map.get(protocol, RuleProtocol.TCP),
            dir_map.get(direction, RuleDirection.INBOUND),
            reason
        )

        if success:
            self.rule_engine.add_bad_port(port)
            self.main_window.show_status_message(message)
        else:
            self.main_window.show_error("Block Failed", message)

    def _delete_rule(self, rule_name: str):
        """Delete a firewall rule."""
        if not is_admin():
            self.main_window.show_error(
                "Admin Required",
                "Deleting rules requires administrator privileges."
            )
            return

        success, message = self.firewall_manager.delete_rule(rule_name)
        if not success:
            self.main_window.show_error("Delete Failed", message)

    def _toggle_rule(self, rule_name: str, enabled: bool):
        """Enable or disable a firewall rule."""
        if not is_admin():
            self.main_window.show_error(
                "Admin Required",
                "Modifying rules requires administrator privileges."
            )
            return

        if enabled:
            success, message = self.firewall_manager.enable_rule(rule_name)
        else:
            success, message = self.firewall_manager.disable_rule(rule_name)

        if success:
            self._refresh_rules()
            self.main_window.show_status_message(message)
        else:
            self.main_window.show_error("Operation Failed", message)

    def _cleanup_rules(self):
        """Remove all firewall rules created by this application."""
        if not is_admin():
            self.main_window.show_error(
                "Admin Required",
                "Cleaning up rules requires administrator privileges."
            )
            return

        success, message = self.firewall_manager.cleanup_all_rules()
        if success:
            self.main_window.show_info("Cleanup Complete", message)
            self._refresh_rules()
        else:
            self.main_window.show_error("Cleanup Failed", message)

    def _refresh_rules(self):
        """Refresh the firewall rules list."""
        rules = self.firewall_manager.get_our_rules()
        self.main_window.update_rules(rules)

    def _save_settings(self, settings: dict):
        """Save application settings."""
        self.config_manager.update(settings)
        self.config = self.config_manager.config

        # Apply new settings
        self.network_monitor.set_poll_interval(self.config.monitor_poll_interval)
        self._apply_rule_settings()

        self.logger.info("system", "Settings saved")

    def _export_logs(self, filename: str, format: str):
        """Export logs to file."""
        entries = self.logger.get_entries(limit=10000)
        success = self.logger.export_to_file(filename, format, entries)

        if success:
            self.logger.info("system", f"Logs exported to {filename}")
        else:
            self.main_window.show_error("Export Failed", "Failed to export logs")

    def _generate_report(self, filename: str):
        """Generate a summary report."""
        success = self.logger.generate_report(filename)

        if success:
            self.logger.info("system", f"Report generated: {filename}")
        else:
            self.main_window.show_error("Report Failed", "Failed to generate report")

    def run(self):
        """Run the application."""
        # Show main window
        self.main_window.show()

        # Refresh rules on startup
        self._refresh_rules()

        # Load log entries
        entries = self.logger.get_entries(limit=100)
        self.main_window.update_logs(entries)

        # Auto-start monitoring if configured
        if self.config.monitor_auto_start:
            QTimer.singleShot(1000, self._start_monitoring)

        self.logger.info("system", "Application started successfully")

        # Run event loop
        return self.app.exec()

    def cleanup(self):
        """Cleanup before exit."""
        self.logger.info("system", "SaadFirewall shutting down...")

        # Stop monitoring
        self.network_monitor.stop()
        self.event_monitor.stop()

        self.logger.info("system", "Shutdown complete")


def main():
    """Main entry point."""
    try:
        app = SaadFirewallApp()
        exit_code = app.run()
        app.cleanup()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

        # Try to show error dialog
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Fatal Error",
                f"Application failed to start:\n\n{str(e)}"
            )
        except Exception:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()
