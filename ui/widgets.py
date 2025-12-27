"""
Custom Widgets Module
Reusable UI components for the application with smooth animations
and glassmorphism styling.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QProgressBar, QGraphicsDropShadowEffect,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QComboBox,
    QSpinBox, QCheckBox, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont


class StatCard(QFrame):
    """
    A card widget for displaying statistics with hover animations.
    Shows a title, value with glassmorphism styling.
    """

    clicked = pyqtSignal()

    def __init__(self, title: str, value: str = "0", color: str = "#ffffff",
                 icon: str = None, parent=None):
        super().__init__(parent)
        self._color = color
        self._original_color = color

        self.setProperty("class", "card")
        self.setMinimumSize(160, 110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        # Title with subtle styling
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            font-size: 10pt;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            background: transparent;
        """)
        layout.addWidget(self.title_label)

        # Value with bold styling
        self.value_label = QLabel(value)
        self._update_value_style()
        layout.addWidget(self.value_label)

        # Add shadow effect for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)

        # Animation for value changes
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate_value_change)
        self._target_value = value
        self._animation_step = 0

    def _update_value_style(self):
        """Update value label styling."""
        self.value_label.setStyleSheet(f"""
            color: {self._color};
            font-size: 32pt;
            font-weight: 700;
            letter-spacing: -1px;
            background: transparent;
        """)

    def enterEvent(self, event):
        """Handle mouse enter with subtle glow."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(255, 255, 255, 30))
        shadow.setOffset(0, 12)
        self.setGraphicsEffect(shadow)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def set_value(self, value: str):
        """Update the displayed value."""
        self.value_label.setText(value)

    def set_color(self, color: str):
        """Update the value color."""
        self._color = color
        self._update_value_style()

    def _animate_value_change(self):
        """Animate value transitions."""
        pass


class AlertBadge(QLabel):
    """
    A badge for showing alert severity with glassmorphism style.
    """

    # Updated colors for glassmorphism theme
    COLORS = {
        'low': '#00ff88',       # Neon green
        'medium': '#ffaa00',    # Amber
        'high': '#ff4466',      # Neon red
        'critical': '#ff00aa'   # Neon magenta
    }

    BG_COLORS = {
        'low': 'rgba(0, 255, 136, 0.15)',
        'medium': 'rgba(255, 170, 0, 0.15)',
        'high': 'rgba(255, 68, 102, 0.15)',
        'critical': 'rgba(255, 0, 170, 0.2)'
    }

    def __init__(self, severity: str = "low", text: str = None, parent=None):
        super().__init__(parent)
        self.set_severity(severity, text)

    def set_severity(self, severity: str, text: str = None):
        """Set the severity level and update appearance."""
        severity = severity.lower()
        color = self.COLORS.get(severity, self.COLORS['low'])
        bg_color = self.BG_COLORS.get(severity, self.BG_COLORS['low'])

        if text is None:
            text = severity.upper()

        self.setText(text)
        self.setStyleSheet(f'''
            background-color: {bg_color};
            color: {color};
            padding: 6px 14px;
            border-radius: 14px;
            border: 1px solid {color};
            font-size: 9pt;
            font-weight: 600;
            letter-spacing: 0.5px;
        ''')
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class SearchBar(QWidget):
    """
    A search bar with filter options.
    """

    search_changed = pyqtSignal(str)
    filter_changed = pyqtSignal(str)

    def __init__(self, placeholder: str = "Search...", filters: list = None, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input, 1)

        # Filter dropdown (optional)
        if filters:
            self.filter_combo = QComboBox()
            self.filter_combo.addItems(filters)
            self.filter_combo.currentTextChanged.connect(self.filter_changed.emit)
            layout.addWidget(self.filter_combo)

        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear)
        layout.addWidget(self.clear_btn)

    def clear(self):
        """Clear the search input."""
        self.search_input.clear()

    def get_text(self) -> str:
        """Get current search text."""
        return self.search_input.text()


class ConnectionTable(QTableWidget):
    """
    Table widget for displaying network connections.
    """

    row_selected = pyqtSignal(dict)
    block_ip_requested = pyqtSignal(str)

    COLUMNS = [
        "Local IP", "Local Port", "Remote IP", "Remote Port",
        "Protocol", "Status", "Process", "PID", "Risk"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()

    def setup_table(self):
        """Configure the table."""
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)

        # Configure header
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        # Set column widths
        self.setColumnWidth(0, 120)  # Local IP
        self.setColumnWidth(1, 80)   # Local Port
        self.setColumnWidth(2, 120)  # Remote IP
        self.setColumnWidth(3, 80)   # Remote Port
        self.setColumnWidth(4, 70)   # Protocol
        self.setColumnWidth(5, 100)  # Status
        self.setColumnWidth(6, 150)  # Process
        self.setColumnWidth(7, 60)   # PID

        # Selection behavior
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Sorting
        self.setSortingEnabled(True)

        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Double-click handler
        self.cellDoubleClicked.connect(self._on_double_click)

    def update_connections(self, connections: list):
        """Update table with new connection data."""
        self.setSortingEnabled(False)
        self.setRowCount(len(connections))

        for row, conn in enumerate(connections):
            self.setItem(row, 0, QTableWidgetItem(str(conn.local_ip)))
            self.setItem(row, 1, QTableWidgetItem(str(conn.local_port)))
            self.setItem(row, 2, QTableWidgetItem(str(conn.remote_ip)))
            self.setItem(row, 3, QTableWidgetItem(str(conn.remote_port)))
            self.setItem(row, 4, QTableWidgetItem(conn.protocol))
            self.setItem(row, 5, QTableWidgetItem(conn.status))
            self.setItem(row, 6, QTableWidgetItem(conn.process_name))
            self.setItem(row, 7, QTableWidgetItem(str(conn.pid)))

            # Risk indicator
            risk = self._calculate_risk(conn)
            risk_item = QTableWidgetItem(risk)
            risk_color = {'LOW': '#4CAF50', 'MEDIUM': '#FF9800', 'HIGH': '#f44336'}
            risk_item.setForeground(QColor(risk_color.get(risk, '#888')))
            self.setItem(row, 8, risk_item)

        self.setSortingEnabled(True)

    def _calculate_risk(self, conn) -> str:
        """Calculate risk level for a connection."""
        # Simple risk calculation
        high_risk_ports = {4444, 5555, 6666, 31337, 12345}
        medium_risk_ports = {8080, 3389, 5900, 22}

        if conn.remote_port in high_risk_ports:
            return "HIGH"
        if conn.remote_port in medium_risk_ports:
            return "MEDIUM"
        if conn.status == "ESTABLISHED" and conn.remote_ip not in ("", "*", "127.0.0.1"):
            return "LOW"
        return "LOW"

    def _show_context_menu(self, pos):
        """Show context menu on right-click."""
        from PyQt6.QtWidgets import QMenu
        item = self.itemAt(pos)
        if not item:
            return

        row = item.row()
        remote_ip = self.item(row, 2).text() if self.item(row, 2) else ""

        if not remote_ip or remote_ip in ("*", "", "127.0.0.1"):
            return

        menu = QMenu(self)
        block_action = menu.addAction(f"Block IP: {remote_ip}")
        block_action.triggered.connect(lambda: self.block_ip_requested.emit(remote_ip))

        menu.addSeparator()
        details_action = menu.addAction("View Details")
        details_action.triggered.connect(lambda: self._show_details(row))

        menu.exec(self.viewport().mapToGlobal(pos))

    def _on_double_click(self, row, col):
        """Handle double-click on a row."""
        self._show_details(row)

    def _show_details(self, row):
        """Show connection details dialog."""
        data = {}
        for col in range(self.columnCount()):
            header = self.horizontalHeaderItem(col).text()
            item = self.item(row, col)
            data[header] = item.text() if item else ""
        self.row_selected.emit(data)


class AlertsList(QTableWidget):
    """
    Table widget for displaying security alerts.
    """

    alert_selected = pyqtSignal(object)
    acknowledge_requested = pyqtSignal(str)
    block_requested = pyqtSignal(str)

    COLUMNS = ["Time", "Severity", "Title", "Process", "IP", "Action"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
        self._alerts = []

    def setup_table(self):
        """Configure the table."""
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 300)
        self.setColumnWidth(3, 120)
        self.setColumnWidth(4, 120)

        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

    def add_alert(self, alert):
        """Add a new alert to the table."""
        self._alerts.insert(0, alert)

        self.insertRow(0)

        # Time
        time_str = alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        self.setItem(0, 0, QTableWidgetItem(time_str))

        # Severity badge
        severity_item = QTableWidgetItem(alert.severity.value.upper())
        colors = {'low': '#4CAF50', 'medium': '#FF9800', 'high': '#f44336', 'critical': '#9C27B0'}
        severity_item.setForeground(QColor(colors.get(alert.severity.value, '#888')))
        self.setItem(0, 1, severity_item)

        # Title
        self.setItem(0, 2, QTableWidgetItem(alert.title))

        # Process
        self.setItem(0, 3, QTableWidgetItem(alert.process_name or "-"))

        # IP
        ip = alert.source_ip or alert.dest_ip or "-"
        self.setItem(0, 4, QTableWidgetItem(ip))

        # Action button
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(4, 4, 4, 4)

        ack_btn = QPushButton("Ack")
        ack_btn.setFixedWidth(50)
        ack_btn.clicked.connect(lambda: self.acknowledge_requested.emit(alert.id))
        action_layout.addWidget(ack_btn)

        if alert.source_ip or alert.dest_ip:
            block_btn = QPushButton("Block")
            block_btn.setFixedWidth(50)
            block_btn.setProperty("class", "danger")
            target_ip = alert.source_ip or alert.dest_ip
            block_btn.clicked.connect(lambda: self.block_requested.emit(target_ip))
            action_layout.addWidget(block_btn)

        self.setCellWidget(0, 5, action_widget)

    def clear_alerts(self):
        """Clear all alerts from the table."""
        self.setRowCount(0)
        self._alerts.clear()


class RulesTable(QTableWidget):
    """
    Table widget for displaying firewall rules.
    """

    delete_requested = pyqtSignal(str)
    toggle_requested = pyqtSignal(str, bool)

    COLUMNS = ["Rule Name", "Direction", "Action", "Address/Port", "Status", "Actions"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()

    def setup_table(self):
        """Configure the table."""
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(3, 150)
        self.setColumnWidth(4, 80)

        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def update_rules(self, rules: list):
        """Update table with firewall rules."""
        self.setRowCount(len(rules))

        for row, rule in enumerate(rules):
            self.setItem(row, 0, QTableWidgetItem(rule.display_name))
            self.setItem(row, 1, QTableWidgetItem(rule.direction.value))
            self.setItem(row, 2, QTableWidgetItem(rule.action.value))

            # Address or port
            target = rule.remote_address or (f"Port {rule.local_port}" if rule.local_port else "-")
            self.setItem(row, 3, QTableWidgetItem(target))

            # Status
            status = "Enabled" if rule.enabled else "Disabled"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor('#4CAF50' if rule.enabled else '#f44336'))
            self.setItem(row, 4, status_item)

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 4, 4, 4)

            toggle_btn = QPushButton("Disable" if rule.enabled else "Enable")
            toggle_btn.setFixedWidth(70)
            toggle_btn.clicked.connect(
                lambda checked, r=rule: self.toggle_requested.emit(r.name, not r.enabled)
            )
            action_layout.addWidget(toggle_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setFixedWidth(60)
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(lambda checked, r=rule: self.delete_requested.emit(r.name))
            action_layout.addWidget(delete_btn)

            self.setCellWidget(row, 5, action_widget)


class BlockIPDialog(QDialog):
    """
    Dialog for blocking an IP address.
    """

    def __init__(self, ip: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Block IP Address")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Form
        form_layout = QFormLayout()

        self.ip_input = QLineEdit(ip)
        self.ip_input.setPlaceholderText("e.g., 192.168.1.100")
        form_layout.addRow("IP Address:", self.ip_input)

        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Both (Inbound + Outbound)", "Inbound Only", "Outbound Only"])
        form_layout.addRow("Direction:", self.direction_combo)

        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Optional reason for blocking")
        form_layout.addRow("Reason:", self.reason_input)

        self.permanent_check = QCheckBox("Permanent block")
        self.permanent_check.setChecked(True)
        form_layout.addRow("", self.permanent_check)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self) -> dict:
        """Get the dialog data."""
        direction_map = {
            "Both (Inbound + Outbound)": "Both",
            "Inbound Only": "Inbound",
            "Outbound Only": "Outbound"
        }
        return {
            'ip': self.ip_input.text().strip(),
            'direction': direction_map[self.direction_combo.currentText()],
            'reason': self.reason_input.text().strip(),
            'permanent': self.permanent_check.isChecked()
        }


class BlockPortDialog(QDialog):
    """
    Dialog for blocking a port.
    """

    def __init__(self, port: int = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Block Port")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Form
        form_layout = QFormLayout()

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        if port:
            self.port_input.setValue(port)
        form_layout.addRow("Port Number:", self.port_input)

        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP", "Both"])
        form_layout.addRow("Protocol:", self.protocol_combo)

        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Inbound", "Outbound", "Both"])
        form_layout.addRow("Direction:", self.direction_combo)

        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Optional reason for blocking")
        form_layout.addRow("Reason:", self.reason_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self) -> dict:
        """Get the dialog data."""
        return {
            'port': self.port_input.value(),
            'protocol': self.protocol_combo.currentText(),
            'direction': self.direction_combo.currentText(),
            'reason': self.reason_input.text().strip()
        }


class LoadingOverlay(QWidget):
    """
    A loading overlay widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Loading...")
        self.label.setStyleSheet("color: white; font-size: 16pt;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setFixedWidth(200)
        layout.addWidget(self.progress)

        self.hide()

    def show_loading(self, message: str = "Loading..."):
        """Show the loading overlay."""
        self.label.setText(message)
        self.resize(self.parent().size())
        self.show()
        self.raise_()

    def hide_loading(self):
        """Hide the loading overlay."""
        self.hide()
