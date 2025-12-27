"""
Settings Page
Application configuration and preferences.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QGroupBox, QCheckBox, QComboBox, QSpinBox,
    QDoubleSpinBox, QLineEdit, QFormLayout, QScrollArea,
    QMessageBox, QFileDialog, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal


class SettingsPage(QWidget):
    """
    Page for application settings.
    """

    settings_changed = pyqtSignal(dict)
    theme_changed = pyqtSignal(str)
    import_config_requested = pyqtSignal(str)
    export_config_requested = pyqtSignal(str)
    reset_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the settings page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Settings")
        title.setProperty("class", "title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Tabs
        tabs = QTabWidget()

        # General settings
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "General")

        # Monitoring settings
        monitoring_tab = self._create_monitoring_tab()
        tabs.addTab(monitoring_tab, "Monitoring")

        # Appearance settings
        appearance_tab = self._create_appearance_tab()
        tabs.addTab(appearance_tab, "Appearance")

        # Logging settings
        logging_tab = self._create_logging_tab()
        tabs.addTab(logging_tab, "Logging")

        # Advanced settings
        advanced_tab = self._create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")

        layout.addWidget(tabs, 1)

        # Bottom buttons
        button_layout = QHBoxLayout()

        import_btn = QPushButton("Import Config")
        import_btn.clicked.connect(self._import_config)
        button_layout.addWidget(import_btn)

        export_btn = QPushButton("Export Config")
        export_btn.clicked.connect(self._export_config)
        button_layout.addWidget(export_btn)

        button_layout.addStretch()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setProperty("class", "danger")
        reset_btn.clicked.connect(self._reset_defaults)
        button_layout.addWidget(reset_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def _create_general_tab(self) -> QWidget:
        """Create general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Application settings
        app_group = QGroupBox("Application")
        app_layout = QFormLayout(app_group)

        self.start_minimized = QCheckBox("Start minimized to tray")
        app_layout.addRow("", self.start_minimized)

        self.minimize_to_tray = QCheckBox("Minimize to system tray")
        self.minimize_to_tray.setChecked(True)
        app_layout.addRow("", self.minimize_to_tray)

        self.show_tray_icon = QCheckBox("Show tray icon")
        self.show_tray_icon.setChecked(True)
        app_layout.addRow("", self.show_tray_icon)

        self.start_with_windows = QCheckBox("Start with Windows")
        app_layout.addRow("", self.start_with_windows)

        layout.addWidget(app_group)

        # Auto-actions
        auto_group = QGroupBox("Automatic Actions")
        auto_layout = QFormLayout(auto_group)

        self.auto_start_monitoring = QCheckBox("Start monitoring on launch")
        self.auto_start_monitoring.setChecked(True)
        auto_layout.addRow("", self.auto_start_monitoring)

        self.auto_block = QCheckBox("Automatically block detected threats")
        auto_layout.addRow("", self.auto_block)

        self.auto_block_duration = QSpinBox()
        self.auto_block_duration.setRange(5, 1440)
        self.auto_block_duration.setValue(30)
        self.auto_block_duration.setSuffix(" minutes")
        auto_layout.addRow("Auto-block duration:", self.auto_block_duration)

        layout.addWidget(auto_group)

        layout.addStretch()
        return widget

    def _create_monitoring_tab(self) -> QWidget:
        """Create monitoring settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Network monitoring
        network_group = QGroupBox("Network Monitoring")
        network_layout = QFormLayout(network_group)

        self.poll_interval = QDoubleSpinBox()
        self.poll_interval.setRange(0.5, 10.0)
        self.poll_interval.setValue(2.0)
        self.poll_interval.setSuffix(" seconds")
        self.poll_interval.setSingleStep(0.5)
        network_layout.addRow("Poll interval:", self.poll_interval)

        self.show_listening = QCheckBox("Show listening ports")
        self.show_listening.setChecked(True)
        network_layout.addRow("", self.show_listening)

        self.show_localhost = QCheckBox("Show localhost connections")
        network_layout.addRow("", self.show_localhost)

        layout.addWidget(network_group)

        # Event log monitoring
        event_group = QGroupBox("Windows Event Log Monitoring")
        event_layout = QFormLayout(event_group)

        self.event_log_enabled = QCheckBox("Enable event log monitoring")
        self.event_log_enabled.setChecked(True)
        event_layout.addRow("", self.event_log_enabled)

        self.event_poll_interval = QSpinBox()
        self.event_poll_interval.setRange(10, 300)
        self.event_poll_interval.setValue(30)
        self.event_poll_interval.setSuffix(" seconds")
        event_layout.addRow("Poll interval:", self.event_poll_interval)

        self.event_lookback = QSpinBox()
        self.event_lookback.setRange(5, 60)
        self.event_lookback.setValue(10)
        self.event_lookback.setSuffix(" minutes")
        event_layout.addRow("Lookback window:", self.event_lookback)

        layout.addWidget(event_group)

        layout.addStretch()
        return widget

    def _create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Theme
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_layout.addRow("Application theme:", self.theme_combo)

        layout.addWidget(theme_group)

        # Font
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 16)
        self.font_size.setValue(10)
        self.font_size.setSuffix(" pt")
        font_layout.addRow("Font size:", self.font_size)

        layout.addWidget(font_group)

        # Alerts appearance
        alerts_group = QGroupBox("Alerts")
        alerts_layout = QFormLayout(alerts_group)

        self.alert_sound = QCheckBox("Enable alert sounds")
        self.alert_sound.setChecked(True)
        alerts_layout.addRow("", self.alert_sound)

        self.alert_notification = QCheckBox("Show desktop notifications")
        self.alert_notification.setChecked(True)
        alerts_layout.addRow("", self.alert_notification)

        self.max_alerts_display = QSpinBox()
        self.max_alerts_display.setRange(10, 500)
        self.max_alerts_display.setValue(100)
        alerts_layout.addRow("Max alerts to display:", self.max_alerts_display)

        layout.addWidget(alerts_group)

        layout.addStretch()
        return widget

    def _create_logging_tab(self) -> QWidget:
        """Create logging settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Log files
        log_group = QGroupBox("Log Files")
        log_layout = QFormLayout(log_group)

        self.log_directory = QLineEdit("logs")
        log_layout.addRow("Log directory:", self.log_directory)

        self.log_max_size = QSpinBox()
        self.log_max_size.setRange(10, 500)
        self.log_max_size.setValue(50)
        self.log_max_size.setSuffix(" MB")
        log_layout.addRow("Max log file size:", self.log_max_size)

        self.log_retention = QSpinBox()
        self.log_retention.setRange(1, 365)
        self.log_retention.setValue(30)
        self.log_retention.setSuffix(" days")
        log_layout.addRow("Log retention:", self.log_retention)

        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level.setCurrentText("INFO")
        log_layout.addRow("Log level:", self.log_level)

        layout.addWidget(log_group)

        # Export settings
        export_group = QGroupBox("Export")
        export_layout = QFormLayout(export_group)

        self.export_format = QComboBox()
        self.export_format.addItems(["Text", "JSON", "CSV"])
        export_layout.addRow("Default export format:", self.export_format)

        layout.addWidget(export_group)

        layout.addStretch()
        return widget

    def _create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Firewall
        fw_group = QGroupBox("Firewall")
        fw_layout = QFormLayout(fw_group)

        self.firewall_prefix = QLineEdit("SaadFirewall_")
        self.firewall_prefix.setEnabled(False)  # Read-only
        fw_layout.addRow("Rule prefix:", self.firewall_prefix)

        layout.addWidget(fw_group)

        # Database
        db_group = QGroupBox("Database")
        db_layout = QFormLayout(db_group)

        self.db_path = QLineEdit("data/alerts.db")
        self.db_path.setEnabled(False)  # Read-only
        db_layout.addRow("Database path:", self.db_path)

        vacuum_btn = QPushButton("Optimize Database")
        vacuum_btn.clicked.connect(self._vacuum_db)
        db_layout.addRow("", vacuum_btn)

        layout.addWidget(db_group)

        # Performance
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)

        info_label = QLabel("Note: Lower poll intervals provide faster updates but use more CPU.")
        info_label.setStyleSheet("color: #888;")
        info_label.setWordWrap(True)
        perf_layout.addRow("", info_label)

        layout.addWidget(perf_group)

        layout.addStretch()
        return widget

    def load_settings(self, config):
        """Load settings from config object."""
        # General
        self.start_minimized.setChecked(config.start_minimized)
        self.minimize_to_tray.setChecked(config.minimize_to_tray)
        self.show_tray_icon.setChecked(config.show_tray_icon)
        self.start_with_windows.setChecked(config.start_with_windows)
        self.auto_start_monitoring.setChecked(config.monitor_auto_start)
        self.auto_block.setChecked(config.firewall_auto_block)
        self.auto_block_duration.setValue(config.firewall_block_duration // 60)

        # Monitoring
        self.poll_interval.setValue(config.monitor_poll_interval)
        self.show_listening.setChecked(config.show_listening_ports)
        self.show_localhost.setChecked(config.show_localhost)
        self.event_log_enabled.setChecked(config.event_log_enabled)
        self.event_poll_interval.setValue(int(config.event_log_poll_interval))
        self.event_lookback.setValue(config.event_log_lookback_minutes)

        # Appearance
        self.theme_combo.setCurrentText(config.theme.capitalize())
        self.font_size.setValue(config.font_size)
        self.alert_sound.setChecked(config.alert_sound_enabled)
        self.alert_notification.setChecked(config.alert_notification_enabled)
        self.max_alerts_display.setValue(config.max_alerts_display)

        # Logging
        self.log_directory.setText(config.log_directory)
        self.log_max_size.setValue(config.log_max_size_mb)
        self.log_retention.setValue(config.log_retention_days)
        self.log_level.setCurrentText(config.log_level)
        self.export_format.setCurrentText(config.export_format.upper())

    def get_settings(self) -> dict:
        """Get current settings as dictionary."""
        return {
            'start_minimized': self.start_minimized.isChecked(),
            'minimize_to_tray': self.minimize_to_tray.isChecked(),
            'show_tray_icon': self.show_tray_icon.isChecked(),
            'start_with_windows': self.start_with_windows.isChecked(),
            'monitor_auto_start': self.auto_start_monitoring.isChecked(),
            'firewall_auto_block': self.auto_block.isChecked(),
            'firewall_block_duration': self.auto_block_duration.value() * 60,
            'monitor_poll_interval': self.poll_interval.value(),
            'show_listening_ports': self.show_listening.isChecked(),
            'show_localhost': self.show_localhost.isChecked(),
            'event_log_enabled': self.event_log_enabled.isChecked(),
            'event_log_poll_interval': float(self.event_poll_interval.value()),
            'event_log_lookback_minutes': self.event_lookback.value(),
            'theme': self.theme_combo.currentText().lower(),
            'font_size': self.font_size.value(),
            'alert_sound_enabled': self.alert_sound.isChecked(),
            'alert_notification_enabled': self.alert_notification.isChecked(),
            'max_alerts_display': self.max_alerts_display.value(),
            'log_directory': self.log_directory.text(),
            'log_max_size_mb': self.log_max_size.value(),
            'log_retention_days': self.log_retention.value(),
            'log_level': self.log_level.currentText(),
            'export_format': self.export_format.currentText().lower()
        }

    def _save_settings(self):
        """Save current settings."""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")

    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self.theme_changed.emit(theme.lower())

    def _import_config(self):
        """Import configuration from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", "", "JSON Files (*.json)"
        )
        if filename:
            self.import_config_requested.emit(filename)

    def _export_config(self):
        """Export configuration to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Configuration", "config_backup.json", "JSON Files (*.json)"
        )
        if filename:
            self.export_config_requested.emit(filename)

    def _reset_defaults(self):
        """Reset to default settings."""
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reset_requested.emit()

    def _vacuum_db(self):
        """Optimize the database."""
        QMessageBox.information(
            self, "Database Optimization",
            "Database optimization has been initiated."
        )
