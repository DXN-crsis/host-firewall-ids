"""
Rules Manager Page
Manages Windows Firewall rules created by the application.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QMessageBox, QTabWidget, QListWidget, QListWidgetItem,
    QSpinBox, QLineEdit, QFormLayout, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from .widgets import RulesTable, BlockIPDialog, BlockPortDialog, SearchBar


class RulesPage(QWidget):
    """
    Page for managing firewall rules and detection settings.
    """

    block_ip_requested = pyqtSignal(dict)
    block_port_requested = pyqtSignal(dict)
    unblock_ip_requested = pyqtSignal(str)
    delete_rule_requested = pyqtSignal(str)
    toggle_rule_requested = pyqtSignal(str, bool)
    cleanup_rules_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    save_detection_settings = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the rules page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Firewall Rules Manager")
        title.setProperty("class", "title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Tab widget
        tabs = QTabWidget()

        # Tab 1: Active Rules
        rules_tab = self._create_rules_tab()
        tabs.addTab(rules_tab, "Firewall Rules")

        # Tab 2: Add Rules
        add_tab = self._create_add_rules_tab()
        tabs.addTab(add_tab, "Add Rules")

        # Tab 3: Detection Settings
        detection_tab = self._create_detection_tab()
        tabs.addTab(detection_tab, "Detection Settings")

        # Tab 4: Bad IPs/Ports
        lists_tab = self._create_lists_tab()
        tabs.addTab(lists_tab, "Threat Lists")

        layout.addWidget(tabs, 1)

    def _create_rules_tab(self) -> QWidget:
        """Create the firewall rules tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)

        # Toolbar
        toolbar = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh Rules")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        toolbar.addWidget(self.refresh_btn)

        toolbar.addStretch()

        self.rule_count_label = QLabel("Rules: 0")
        toolbar.addWidget(self.rule_count_label)

        self.cleanup_btn = QPushButton("Cleanup All Rules")
        self.cleanup_btn.setProperty("class", "danger")
        self.cleanup_btn.clicked.connect(self._on_cleanup_clicked)
        toolbar.addWidget(self.cleanup_btn)

        layout.addLayout(toolbar)

        # Rules table
        self.rules_table = RulesTable()
        self.rules_table.delete_requested.connect(self._on_delete_rule)
        self.rules_table.toggle_requested.connect(self.toggle_rule_requested.emit)
        layout.addWidget(self.rules_table)

        return widget

    def _create_add_rules_tab(self) -> QWidget:
        """Create the add rules tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)

        # Block IP section
        ip_group = QGroupBox("Block IP Address")
        ip_layout = QVBoxLayout(ip_group)

        ip_form = QFormLayout()

        self.block_ip_input = QLineEdit()
        self.block_ip_input.setPlaceholderText("e.g., 192.168.1.100 or 10.0.0.0/24")
        ip_form.addRow("IP Address:", self.block_ip_input)

        from PyQt6.QtWidgets import QComboBox
        self.ip_direction_combo = QComboBox()
        self.ip_direction_combo.addItems(["Both", "Inbound", "Outbound"])
        ip_form.addRow("Direction:", self.ip_direction_combo)

        self.ip_reason_input = QLineEdit()
        self.ip_reason_input.setPlaceholderText("Reason for blocking (optional)")
        ip_form.addRow("Reason:", self.ip_reason_input)

        ip_layout.addLayout(ip_form)

        block_ip_btn = QPushButton("Block IP")
        block_ip_btn.setProperty("class", "danger")
        block_ip_btn.clicked.connect(self._on_block_ip)
        ip_layout.addWidget(block_ip_btn)

        layout.addWidget(ip_group)

        # Block Port section
        port_group = QGroupBox("Block Port")
        port_layout = QVBoxLayout(port_group)

        port_form = QFormLayout()

        self.block_port_input = QSpinBox()
        self.block_port_input.setRange(1, 65535)
        self.block_port_input.setValue(4444)
        port_form.addRow("Port Number:", self.block_port_input)

        self.port_protocol_combo = QComboBox()
        self.port_protocol_combo.addItems(["TCP", "UDP"])
        port_form.addRow("Protocol:", self.port_protocol_combo)

        self.port_direction_combo = QComboBox()
        self.port_direction_combo.addItems(["Inbound", "Outbound"])
        port_form.addRow("Direction:", self.port_direction_combo)

        self.port_reason_input = QLineEdit()
        self.port_reason_input.setPlaceholderText("Reason for blocking (optional)")
        port_form.addRow("Reason:", self.port_reason_input)

        port_layout.addLayout(port_form)

        block_port_btn = QPushButton("Block Port")
        block_port_btn.setProperty("class", "danger")
        block_port_btn.clicked.connect(self._on_block_port)
        port_layout.addWidget(block_port_btn)

        layout.addWidget(port_group)

        layout.addStretch()

        return widget

    def _create_detection_tab(self) -> QWidget:
        """Create the detection settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Beaconing Detection
        beacon_group = QGroupBox("Beaconing Detection (R001)")
        beacon_layout = QFormLayout(beacon_group)

        self.beacon_enabled = QCheckBox("Enabled")
        self.beacon_enabled.setChecked(True)
        beacon_layout.addRow("", self.beacon_enabled)

        self.beacon_threshold = QSpinBox()
        self.beacon_threshold.setRange(5, 100)
        self.beacon_threshold.setValue(20)
        beacon_layout.addRow("Threshold (unique IPs):", self.beacon_threshold)

        self.beacon_window = QSpinBox()
        self.beacon_window.setRange(10, 300)
        self.beacon_window.setValue(60)
        beacon_layout.addRow("Time Window (seconds):", self.beacon_window)

        scroll_layout.addWidget(beacon_group)

        # Bad Port Detection
        port_group = QGroupBox("Suspicious Port Detection (R002)")
        port_layout = QFormLayout(port_group)

        self.bad_port_enabled = QCheckBox("Enabled")
        self.bad_port_enabled.setChecked(True)
        port_layout.addRow("", self.bad_port_enabled)

        scroll_layout.addWidget(port_group)

        # High Connection Rate
        rate_group = QGroupBox("High Connection Rate Detection (R003)")
        rate_layout = QFormLayout(rate_group)

        self.rate_enabled = QCheckBox("Enabled")
        self.rate_enabled.setChecked(True)
        rate_layout.addRow("", self.rate_enabled)

        self.rate_threshold = QSpinBox()
        self.rate_threshold.setRange(10, 200)
        self.rate_threshold.setValue(50)
        rate_layout.addRow("Threshold (connections):", self.rate_threshold)

        scroll_layout.addWidget(rate_group)

        # Failed Login Detection
        login_group = QGroupBox("Failed Login Detection (R004)")
        login_layout = QFormLayout(login_group)

        self.login_enabled = QCheckBox("Enabled")
        self.login_enabled.setChecked(True)
        login_layout.addRow("", self.login_enabled)

        self.login_threshold = QSpinBox()
        self.login_threshold.setRange(3, 50)
        self.login_threshold.setValue(5)
        login_layout.addRow("Threshold (attempts):", self.login_threshold)

        self.login_window = QSpinBox()
        self.login_window.setRange(60, 3600)
        self.login_window.setValue(600)
        login_layout.addRow("Time Window (seconds):", self.login_window)

        scroll_layout.addWidget(login_group)

        # Port Scan Detection
        scan_group = QGroupBox("Port Scan Detection (R006)")
        scan_layout = QFormLayout(scan_group)

        self.scan_enabled = QCheckBox("Enabled")
        self.scan_enabled.setChecked(True)
        scan_layout.addRow("", self.scan_enabled)

        self.scan_threshold = QSpinBox()
        self.scan_threshold.setRange(5, 50)
        self.scan_threshold.setValue(10)
        scan_layout.addRow("Threshold (ports):", self.scan_threshold)

        scroll_layout.addWidget(scan_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Save button
        save_btn = QPushButton("Save Detection Settings")
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self._on_save_detection)
        layout.addWidget(save_btn)

        return widget

    def _create_lists_tab(self) -> QWidget:
        """Create the threat lists tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)

        # Bad IPs list
        ips_group = QGroupBox("Bad IPs (Threat Intelligence)")
        ips_layout = QVBoxLayout(ips_group)

        self.bad_ips_list = QListWidget()
        ips_layout.addWidget(self.bad_ips_list)

        ips_input_layout = QHBoxLayout()
        self.new_bad_ip_input = QLineEdit()
        self.new_bad_ip_input.setPlaceholderText("Enter IP address")
        ips_input_layout.addWidget(self.new_bad_ip_input)

        add_ip_btn = QPushButton("Add")
        add_ip_btn.clicked.connect(self._add_bad_ip)
        ips_input_layout.addWidget(add_ip_btn)

        remove_ip_btn = QPushButton("Remove Selected")
        remove_ip_btn.clicked.connect(self._remove_bad_ip)
        ips_input_layout.addWidget(remove_ip_btn)

        ips_layout.addLayout(ips_input_layout)

        layout.addWidget(ips_group)

        # Bad Ports list
        ports_group = QGroupBox("Suspicious Ports")
        ports_layout = QVBoxLayout(ports_group)

        self.bad_ports_list = QListWidget()
        ports_layout.addWidget(self.bad_ports_list)

        ports_input_layout = QHBoxLayout()
        self.new_bad_port_input = QSpinBox()
        self.new_bad_port_input.setRange(1, 65535)
        ports_input_layout.addWidget(self.new_bad_port_input)

        add_port_btn = QPushButton("Add")
        add_port_btn.clicked.connect(self._add_bad_port)
        ports_input_layout.addWidget(add_port_btn)

        remove_port_btn = QPushButton("Remove Selected")
        remove_port_btn.clicked.connect(self._remove_bad_port)
        ports_input_layout.addWidget(remove_port_btn)

        ports_layout.addLayout(ports_input_layout)

        layout.addWidget(ports_group)

        return widget

    def update_rules(self, rules: list):
        """Update the rules table."""
        self.rules_table.update_rules(rules)
        self.rule_count_label.setText(f"Rules: {len(rules)}")

    def update_bad_ips(self, ips: list):
        """Update the bad IPs list."""
        self.bad_ips_list.clear()
        for ip in ips:
            self.bad_ips_list.addItem(QListWidgetItem(ip))

    def update_bad_ports(self, ports: list):
        """Update the bad ports list."""
        self.bad_ports_list.clear()
        for port in ports:
            self.bad_ports_list.addItem(QListWidgetItem(str(port)))

    def update_detection_settings(self, settings: dict):
        """Update detection settings UI from config."""
        self.beacon_enabled.setChecked(settings.get('R001', {}).get('enabled', True))
        self.beacon_threshold.setValue(settings.get('R001', {}).get('threshold', 20))
        self.beacon_window.setValue(settings.get('R001', {}).get('time_window', 60))

        self.bad_port_enabled.setChecked(settings.get('R002', {}).get('enabled', True))

        self.rate_enabled.setChecked(settings.get('R003', {}).get('enabled', True))
        self.rate_threshold.setValue(settings.get('R003', {}).get('threshold', 50))

        self.login_enabled.setChecked(settings.get('R004', {}).get('enabled', True))
        self.login_threshold.setValue(settings.get('R004', {}).get('threshold', 5))
        self.login_window.setValue(settings.get('R004', {}).get('time_window', 600))

        self.scan_enabled.setChecked(settings.get('R006', {}).get('enabled', True))
        self.scan_threshold.setValue(settings.get('R006', {}).get('threshold', 10))

    def _on_block_ip(self):
        """Handle block IP button click."""
        ip = self.block_ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Error", "Please enter an IP address.")
            return

        data = {
            'ip': ip,
            'direction': self.ip_direction_combo.currentText(),
            'reason': self.ip_reason_input.text().strip()
        }
        self.block_ip_requested.emit(data)
        self.block_ip_input.clear()
        self.ip_reason_input.clear()

    def _on_block_port(self):
        """Handle block port button click."""
        data = {
            'port': self.block_port_input.value(),
            'protocol': self.port_protocol_combo.currentText(),
            'direction': self.port_direction_combo.currentText(),
            'reason': self.port_reason_input.text().strip()
        }
        self.block_port_requested.emit(data)
        self.port_reason_input.clear()

    def _on_delete_rule(self, rule_name: str):
        """Handle delete rule request."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the rule:\n{rule_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_rule_requested.emit(rule_name)

    def _on_cleanup_clicked(self):
        """Handle cleanup all rules button click."""
        reply = QMessageBox.warning(
            self, "Confirm Cleanup",
            "This will delete ALL firewall rules created by this application.\n\nAre you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup_rules_requested.emit()

    def _on_save_detection(self):
        """Handle save detection settings."""
        settings = {
            'R001': {
                'enabled': self.beacon_enabled.isChecked(),
                'threshold': self.beacon_threshold.value(),
                'time_window': self.beacon_window.value()
            },
            'R002': {
                'enabled': self.bad_port_enabled.isChecked()
            },
            'R003': {
                'enabled': self.rate_enabled.isChecked(),
                'threshold': self.rate_threshold.value()
            },
            'R004': {
                'enabled': self.login_enabled.isChecked(),
                'threshold': self.login_threshold.value(),
                'time_window': self.login_window.value()
            },
            'R006': {
                'enabled': self.scan_enabled.isChecked(),
                'threshold': self.scan_threshold.value()
            }
        }
        self.save_detection_settings.emit(settings)
        QMessageBox.information(self, "Success", "Detection settings saved.")

    def _add_bad_ip(self):
        """Add IP to bad IPs list."""
        ip = self.new_bad_ip_input.text().strip()
        if ip:
            self.bad_ips_list.addItem(QListWidgetItem(ip))
            self.new_bad_ip_input.clear()

    def _remove_bad_ip(self):
        """Remove selected IP from bad IPs list."""
        current = self.bad_ips_list.currentRow()
        if current >= 0:
            self.bad_ips_list.takeItem(current)

    def _add_bad_port(self):
        """Add port to bad ports list."""
        port = self.new_bad_port_input.value()
        self.bad_ports_list.addItem(QListWidgetItem(str(port)))

    def _remove_bad_port(self):
        """Remove selected port from bad ports list."""
        current = self.bad_ports_list.currentRow()
        if current >= 0:
            self.bad_ports_list.takeItem(current)

    def get_bad_ips(self) -> list:
        """Get list of bad IPs."""
        return [self.bad_ips_list.item(i).text()
                for i in range(self.bad_ips_list.count())]

    def get_bad_ports(self) -> list:
        """Get list of bad ports."""
        return [int(self.bad_ports_list.item(i).text())
                for i in range(self.bad_ports_list.count())]
