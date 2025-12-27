"""
Dashboard Page
Main view showing real-time network connections and statistics.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from .widgets import StatCard, ConnectionTable, SearchBar, BlockIPDialog


class Dashboard(QWidget):
    """
    Dashboard page showing real-time network monitoring.
    """

    block_ip_requested = pyqtSignal(str)
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self._connections = []
        self._stats = {}

    def setup_ui(self):
        """Setup the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Network Dashboard")
        title.setProperty("class", "title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("class", "primary")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)

        # Status indicator
        self.status_label = QLabel("Monitoring: Active")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        # Stats cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        self.total_conn_card = StatCard("Total Connections", "0", "#2196F3")
        stats_layout.addWidget(self.total_conn_card)

        self.established_card = StatCard("Established", "0", "#4CAF50")
        stats_layout.addWidget(self.established_card)

        self.unique_ips_card = StatCard("Unique Remote IPs", "0", "#FF9800")
        stats_layout.addWidget(self.unique_ips_card)

        self.alerts_card = StatCard("Active Alerts", "0", "#f44336")
        stats_layout.addWidget(self.alerts_card)

        layout.addLayout(stats_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Connections table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Search bar
        self.search_bar = SearchBar(
            placeholder="Search by IP, port, or process...",
            filters=["All", "TCP", "UDP", "Established", "Listening"]
        )
        self.search_bar.search_changed.connect(self._filter_connections)
        self.search_bar.filter_changed.connect(self._filter_connections)
        left_layout.addWidget(self.search_bar)

        # Connections table
        self.connections_table = ConnectionTable()
        self.connections_table.block_ip_requested.connect(self._on_block_ip)
        self.connections_table.row_selected.connect(self._on_connection_selected)
        left_layout.addWidget(self.connections_table)

        splitter.addWidget(left_widget)

        # Right side - Top IPs and Ports
        right_widget = QWidget()
        right_widget.setMaximumWidth(350)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)

        # Top Remote IPs
        top_ips_group = QGroupBox("Top Remote IPs")
        top_ips_layout = QVBoxLayout(top_ips_group)

        self.top_ips_table = QTableWidget()
        self.top_ips_table.setColumnCount(3)
        self.top_ips_table.setHorizontalHeaderLabels(["IP", "Count", "Action"])
        self.top_ips_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.top_ips_table.setMaximumHeight(200)
        top_ips_layout.addWidget(self.top_ips_table)

        right_layout.addWidget(top_ips_group)

        # Top Ports
        top_ports_group = QGroupBox("Most Used Ports")
        top_ports_layout = QVBoxLayout(top_ports_group)

        self.top_ports_table = QTableWidget()
        self.top_ports_table.setColumnCount(2)
        self.top_ports_table.setHorizontalHeaderLabels(["Port", "Count"])
        self.top_ports_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.top_ports_table.setMaximumHeight(200)
        top_ports_layout.addWidget(self.top_ports_table)

        right_layout.addWidget(top_ports_group)

        # Top Processes
        top_procs_group = QGroupBox("Top Processes")
        top_procs_layout = QVBoxLayout(top_procs_group)

        self.top_procs_table = QTableWidget()
        self.top_procs_table.setColumnCount(2)
        self.top_procs_table.setHorizontalHeaderLabels(["Process", "Connections"])
        self.top_procs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.top_procs_table.setMaximumHeight(200)
        top_procs_layout.addWidget(self.top_procs_table)

        right_layout.addWidget(top_procs_group)

        right_layout.addStretch()

        splitter.addWidget(right_widget)

        # Set splitter sizes
        splitter.setSizes([700, 350])

        layout.addWidget(splitter, 1)

        # Footer with last update time
        footer_layout = QHBoxLayout()
        self.last_update_label = QLabel("Last update: --")
        self.last_update_label.setStyleSheet("color: #888;")
        footer_layout.addWidget(self.last_update_label)
        footer_layout.addStretch()

        self.connection_rate_label = QLabel("Connection rate: -- /sec")
        self.connection_rate_label.setStyleSheet("color: #888;")
        footer_layout.addWidget(self.connection_rate_label)

        layout.addLayout(footer_layout)

    def update_connections(self, connections: list):
        """Update the connections table with new data."""
        from datetime import datetime

        self._connections = connections
        self._apply_filter()
        self.last_update_label.setText(f"Last update: {datetime.now().strftime('%H:%M:%S')}")

    def update_stats(self, stats: dict):
        """Update statistics displays."""
        self._stats = stats

        self.total_conn_card.set_value(str(stats.get('total_connections', 0)))
        self.established_card.set_value(str(stats.get('established_count', 0)))
        self.unique_ips_card.set_value(str(stats.get('unique_remote_ips', 0)))

        # Update top IPs table
        top_ips = stats.get('top_remote_ips', {})
        self.top_ips_table.setRowCount(min(len(top_ips), 10))
        for row, (ip, count) in enumerate(list(top_ips.items())[:10]):
            self.top_ips_table.setItem(row, 0, QTableWidgetItem(ip))
            self.top_ips_table.setItem(row, 1, QTableWidgetItem(str(count)))

            # Block button
            block_btn = QPushButton("Block")
            block_btn.setFixedWidth(60)
            block_btn.clicked.connect(lambda checked, i=ip: self._on_block_ip(i))
            self.top_ips_table.setCellWidget(row, 2, block_btn)

        # Update top ports table
        top_ports = stats.get('top_ports', {})
        self.top_ports_table.setRowCount(min(len(top_ports), 10))
        for row, (port, count) in enumerate(list(top_ports.items())[:10]):
            self.top_ports_table.setItem(row, 0, QTableWidgetItem(str(port)))
            self.top_ports_table.setItem(row, 1, QTableWidgetItem(str(count)))

        # Update top processes table
        top_procs = stats.get('top_processes', {})
        self.top_procs_table.setRowCount(min(len(top_procs), 10))
        for row, (proc, count) in enumerate(list(top_procs.items())[:10]):
            self.top_procs_table.setItem(row, 0, QTableWidgetItem(proc))
            self.top_procs_table.setItem(row, 1, QTableWidgetItem(str(count)))

    def update_alert_count(self, count: int):
        """Update the alerts count card."""
        self.alerts_card.set_value(str(count))
        if count > 0:
            self.alerts_card.set_color("#f44336")
        else:
            self.alerts_card.set_color("#4CAF50")

    def set_monitoring_status(self, active: bool):
        """Update the monitoring status indicator."""
        if active:
            self.status_label.setText("Monitoring: Active")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.status_label.setText("Monitoring: Paused")
            self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")

    def _filter_connections(self):
        """Apply search and filter to connections."""
        self._apply_filter()

    def _apply_filter(self):
        """Apply current filter to connections table."""
        search_text = self.search_bar.get_text().lower()
        filter_type = self.search_bar.filter_combo.currentText() if hasattr(self.search_bar, 'filter_combo') else "All"

        filtered = []
        for conn in self._connections:
            # Apply type filter
            if filter_type == "TCP" and conn.protocol != "TCP":
                continue
            if filter_type == "UDP" and conn.protocol != "UDP":
                continue
            if filter_type == "Established" and conn.status != "ESTABLISHED":
                continue
            if filter_type == "Listening" and conn.status != "LISTEN":
                continue

            # Apply search filter
            if search_text:
                searchable = f"{conn.local_ip} {conn.local_port} {conn.remote_ip} {conn.remote_port} {conn.process_name}".lower()
                if search_text not in searchable:
                    continue

            filtered.append(conn)

        self.connections_table.update_connections(filtered)

    def _on_block_ip(self, ip: str):
        """Handle block IP request."""
        dialog = BlockIPDialog(ip, self)
        if dialog.exec():
            data = dialog.get_data()
            self.block_ip_requested.emit(data['ip'])

    def _on_connection_selected(self, data: dict):
        """Handle connection selection."""
        # Show details in a message box
        details = "\n".join([f"{k}: {v}" for k, v in data.items()])
        QMessageBox.information(self, "Connection Details", details)
