"""
Main Window
Application shell with navigation sidebar and page container.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QStackedWidget, QMessageBox, QSystemTrayIcon, QMenu,
    QApplication, QSplitter, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QAction, QCloseEvent

from .dashboard import Dashboard
from .rules_page import RulesPage
from .alerts_page import AlertsPage
from .logs_page import LogsPage
from .settings_page import SettingsPage
from .about_page import AboutPage
from .styles import Styles, apply_theme


class NavigationButton(QPushButton):
    """Custom navigation button for the sidebar."""

    def __init__(self, text: str, icon_char: str = None, parent=None):
        super().__init__(parent)
        self.setText(f"  {icon_char}  {text}" if icon_char else text)
        self.setProperty("class", "nav-button")
        self.setCheckable(True)
        self.setMinimumHeight(45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class MainWindow(QMainWindow):
    """
    Main application window.
    """

    # Signals for communicating with the application
    start_monitoring = pyqtSignal()
    stop_monitoring = pyqtSignal()
    block_ip = pyqtSignal(str, str, str)  # ip, direction, reason
    block_port = pyqtSignal(int, str, str, str)  # port, protocol, direction, reason
    unblock_ip = pyqtSignal(str)
    delete_rule = pyqtSignal(str)
    toggle_rule = pyqtSignal(str, bool)
    cleanup_rules = pyqtSignal()
    refresh_rules = pyqtSignal()
    save_settings = pyqtSignal(dict)
    export_logs = pyqtSignal(str, str)
    generate_report = pyqtSignal(str)

    def __init__(self, config=None):
        super().__init__()
        self.config = config
        self._is_monitoring = False

        self.setWindowTitle("SaadFirewall - Smart Host Firewall + IDS")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Setup UI
        self._setup_ui()
        self._setup_tray_icon()
        self._connect_signals()

        # Apply theme
        if config:
            apply_theme(QApplication.instance(), config.theme)

    def _setup_ui(self):
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Page stack
        self.page_stack = QStackedWidget()

        # Create pages
        self.dashboard = Dashboard()
        self.rules_page = RulesPage()
        self.alerts_page = AlertsPage()
        self.logs_page = LogsPage()
        self.settings_page = SettingsPage()
        self.about_page = AboutPage()

        self.page_stack.addWidget(self.dashboard)
        self.page_stack.addWidget(self.rules_page)
        self.page_stack.addWidget(self.alerts_page)
        self.page_stack.addWidget(self.logs_page)
        self.page_stack.addWidget(self.settings_page)
        self.page_stack.addWidget(self.about_page)

        content_layout.addWidget(self.page_stack)

        main_layout.addWidget(content_widget, 1)

        # Status bar
        self._setup_status_bar()

    def _create_sidebar(self) -> QFrame:
        """Create the navigation sidebar."""
        sidebar = QFrame()
        sidebar.setProperty("class", "sidebar")
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # App title
        title = QLabel("SaadFirewall")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2196F3; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(20)

        # Navigation buttons
        self.nav_buttons = []

        self.nav_dashboard = NavigationButton("Dashboard", "📊")
        self.nav_dashboard.setChecked(True)
        self.nav_dashboard.clicked.connect(lambda: self._navigate_to(0))
        layout.addWidget(self.nav_dashboard)
        self.nav_buttons.append(self.nav_dashboard)

        self.nav_rules = NavigationButton("Rules", "🛡️")
        self.nav_rules.clicked.connect(lambda: self._navigate_to(1))
        layout.addWidget(self.nav_rules)
        self.nav_buttons.append(self.nav_rules)

        self.nav_alerts = NavigationButton("Alerts", "⚠️")
        self.nav_alerts.clicked.connect(lambda: self._navigate_to(2))
        layout.addWidget(self.nav_alerts)
        self.nav_buttons.append(self.nav_alerts)

        self.nav_logs = NavigationButton("Logs", "📋")
        self.nav_logs.clicked.connect(lambda: self._navigate_to(3))
        layout.addWidget(self.nav_logs)
        self.nav_buttons.append(self.nav_logs)

        self.nav_settings = NavigationButton("Settings", "⚙️")
        self.nav_settings.clicked.connect(lambda: self._navigate_to(4))
        layout.addWidget(self.nav_settings)
        self.nav_buttons.append(self.nav_settings)

        self.nav_about = NavigationButton("About", "ℹ️")
        self.nav_about.clicked.connect(lambda: self._navigate_to(5))
        layout.addWidget(self.nav_about)
        self.nav_buttons.append(self.nav_about)

        layout.addStretch()

        # Monitoring control
        control_frame = QFrame()
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(5, 10, 5, 10)

        self.monitoring_status = QLabel("Monitoring: Stopped")
        self.monitoring_status.setStyleSheet("color: #888; font-size: 9pt;")
        self.monitoring_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.monitoring_status)

        self.toggle_btn = QPushButton("Start Monitoring")
        self.toggle_btn.setProperty("class", "primary")
        self.toggle_btn.clicked.connect(self._toggle_monitoring)
        control_layout.addWidget(self.toggle_btn)

        layout.addWidget(control_frame)

        return sidebar

    def _setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        self.status_bar.addPermanentWidget(QLabel("|"))

        self.connection_count_label = QLabel("Connections: 0")
        self.status_bar.addPermanentWidget(self.connection_count_label)

        self.status_bar.addPermanentWidget(QLabel("|"))

        self.alert_count_label = QLabel("Alerts: 0")
        self.status_bar.addPermanentWidget(self.alert_count_label)

        self.status_bar.addPermanentWidget(QLabel("|"))

        self.admin_label = QLabel("Admin: Checking...")
        self.status_bar.addPermanentWidget(self.admin_label)

    def _setup_tray_icon(self):
        """Setup system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        self.tray_toggle_action = QAction("Start Monitoring", self)
        self.tray_toggle_action.triggered.connect(self._toggle_monitoring)
        tray_menu.addAction(self.tray_toggle_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Set icon (using a simple colored square as placeholder)
        # In production, you would use a proper icon file
        self.tray_icon.setToolTip("SaadFirewall")

    def _connect_signals(self):
        """Connect page signals to main window signals."""
        # Dashboard
        self.dashboard.block_ip_requested.connect(self._on_block_ip_request)
        self.dashboard.refresh_requested.connect(self.refresh_rules.emit)

        # Rules page
        self.rules_page.block_ip_requested.connect(
            lambda data: self._on_block_ip_full(data)
        )
        self.rules_page.block_port_requested.connect(
            lambda data: self._on_block_port(data)
        )
        self.rules_page.delete_rule_requested.connect(self.delete_rule.emit)
        self.rules_page.toggle_rule_requested.connect(self.toggle_rule.emit)
        self.rules_page.cleanup_rules_requested.connect(self.cleanup_rules.emit)
        self.rules_page.refresh_requested.connect(self.refresh_rules.emit)

        # Alerts page
        self.alerts_page.block_ip_requested.connect(self._on_block_ip_request)

        # Logs page
        self.logs_page.export_requested.connect(self.export_logs.emit)
        self.logs_page.generate_report_requested.connect(self.generate_report.emit)

        # Settings page
        self.settings_page.settings_changed.connect(self.save_settings.emit)
        self.settings_page.theme_changed.connect(
            lambda theme: apply_theme(QApplication.instance(), theme)
        )

    def _navigate_to(self, index: int):
        """Navigate to a page by index."""
        self.page_stack.setCurrentIndex(index)

        # Update navigation button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def _toggle_monitoring(self):
        """Toggle network monitoring."""
        if self._is_monitoring:
            self.stop_monitoring.emit()
        else:
            self.start_monitoring.emit()

    def set_monitoring_state(self, is_running: bool):
        """Update UI to reflect monitoring state."""
        self._is_monitoring = is_running

        if is_running:
            self.toggle_btn.setText("Stop Monitoring")
            self.toggle_btn.setStyleSheet("background-color: #f44336;")
            self.monitoring_status.setText("Monitoring: Active")
            self.monitoring_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.tray_toggle_action.setText("Stop Monitoring")
            self.dashboard.set_monitoring_status(True)
        else:
            self.toggle_btn.setText("Start Monitoring")
            self.toggle_btn.setStyleSheet("")
            self.monitoring_status.setText("Monitoring: Stopped")
            self.monitoring_status.setStyleSheet("color: #888;")
            self.tray_toggle_action.setText("Start Monitoring")
            self.dashboard.set_monitoring_status(False)

    def set_admin_status(self, is_admin: bool):
        """Update admin status display."""
        if is_admin:
            self.admin_label.setText("Admin: Yes")
            self.admin_label.setStyleSheet("color: #4CAF50;")
        else:
            self.admin_label.setText("Admin: No (Limited)")
            self.admin_label.setStyleSheet("color: #FF9800;")

    def update_connections(self, connections: list):
        """Update dashboard with connection data."""
        self.dashboard.update_connections(connections)
        self.connection_count_label.setText(f"Connections: {len(connections)}")

    def update_stats(self, stats: dict):
        """Update dashboard statistics."""
        self.dashboard.update_stats(stats)

    def update_rules(self, rules: list):
        """Update rules page with firewall rules."""
        self.rules_page.update_rules(rules)

    def add_alert(self, alert):
        """Add a new security alert."""
        self.alerts_page.add_alert(alert)

        # Update alert count in status bar and navigation
        count = self.alerts_page.get_unacknowledged_count()
        self.alert_count_label.setText(f"Alerts: {count}")
        self.dashboard.update_alert_count(count)

        if count > 0:
            self.nav_alerts.setText(f"  ⚠️  Alerts ({count})")
        else:
            self.nav_alerts.setText("  ⚠️  Alerts")

        # Show notification
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                "Security Alert",
                alert.title,
                QSystemTrayIcon.MessageIcon.Warning,
                3000
            )

    def update_logs(self, entries: list):
        """Update logs page with log entries."""
        self.logs_page.update_logs(entries)

    def show_status_message(self, message: str, timeout: int = 3000):
        """Show a temporary status message."""
        self.status_label.setText(message)
        QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))

    def show_error(self, title: str, message: str):
        """Show an error message dialog."""
        QMessageBox.critical(self, title, message)

    def show_info(self, title: str, message: str):
        """Show an information message dialog."""
        QMessageBox.information(self, title, message)

    def _on_block_ip_request(self, ip: str):
        """Handle simple block IP request."""
        self.block_ip.emit(ip, "Both", "Blocked from dashboard")

    def _on_block_ip_full(self, data: dict):
        """Handle full block IP request with options."""
        self.block_ip.emit(data['ip'], data['direction'], data.get('reason', ''))

    def _on_block_port(self, data: dict):
        """Handle block port request."""
        self.block_port.emit(
            data['port'],
            data['protocol'],
            data['direction'],
            data.get('reason', '')
        )

    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()

    def closeEvent(self, event: QCloseEvent):
        """Handle window close event."""
        if self.config and self.config.minimize_to_tray:
            event.ignore()
            self.hide()
            if hasattr(self, 'tray_icon'):
                self.tray_icon.show()
        else:
            # Confirm exit
            reply = QMessageBox.question(
                self, "Confirm Exit",
                "Are you sure you want to exit SaadFirewall?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()

    def show_admin_required_dialog(self):
        """Show dialog explaining admin requirements."""
        QMessageBox.warning(
            self,
            "Administrator Privileges Required",
            "Some features require Administrator privileges:\n\n"
            "- Creating/deleting firewall rules\n"
            "- Reading Windows Security Event Log\n\n"
            "Please restart the application as Administrator for full functionality.\n\n"
            "Right-click the application and select 'Run as administrator'."
        )

    def load_settings(self, config):
        """Load settings into settings page."""
        self.config = config
        self.settings_page.load_settings(config)
