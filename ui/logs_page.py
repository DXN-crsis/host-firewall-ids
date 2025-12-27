"""
Logs Page
Browse and export application logs.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QMessageBox, QFileDialog, QDateEdit, QComboBox,
    QLineEdit, QCheckBox, QSplitter, QTextEdit, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate

from datetime import datetime, timedelta


class LogsPage(QWidget):
    """
    Page for viewing and exporting logs.
    """

    export_requested = pyqtSignal(str, str)  # filename, format
    generate_report_requested = pyqtSignal(str)  # filename

    def __init__(self, parent=None):
        super().__init__(parent)
        self._log_entries = []
        self.setup_ui()

    def setup_ui(self):
        """Setup the logs page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Logs & Reports")
        title.setProperty("class", "title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)

        # Date range
        filter_layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.date_to)

        # Severity filter
        filter_layout.addWidget(QLabel("Severity:"))
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "ALERT"])
        filter_layout.addWidget(self.severity_filter)

        # Category filter
        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All", "connection", "firewall", "security", "rule_engine", "general"])
        filter_layout.addWidget(self.category_filter)

        # Search
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search logs...")
        filter_layout.addWidget(self.search_input, 1)

        # Apply button
        apply_btn = QPushButton("Apply Filters")
        apply_btn.clicked.connect(self._apply_filters)
        filter_layout.addWidget(apply_btn)

        layout.addWidget(filter_group)

        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels([
            "Timestamp", "Level", "Category", "Message", "Details"
        ])

        header = self.logs_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        self.logs_table.setColumnWidth(0, 160)
        self.logs_table.setColumnWidth(1, 80)
        self.logs_table.setColumnWidth(2, 100)
        self.logs_table.setColumnWidth(3, 400)

        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.logs_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.logs_table.cellClicked.connect(self._on_log_selected)

        layout.addWidget(self.logs_table, 1)

        # Log details
        details_group = QGroupBox("Log Details")
        details_layout = QVBoxLayout(details_group)

        self.log_details = QTextEdit()
        self.log_details.setReadOnly(True)
        self.log_details.setMaximumHeight(150)
        self.log_details.setPlaceholderText("Select a log entry to view details...")
        details_layout.addWidget(self.log_details)

        layout.addWidget(details_group)

        # Export section
        export_layout = QHBoxLayout()

        export_layout.addWidget(QLabel("Export Format:"))
        self.export_format = QComboBox()
        self.export_format.addItems(["Text (.txt)", "JSON (.json)", "CSV (.csv)", "JSON Lines (.jsonl)"])
        export_layout.addWidget(self.export_format)

        export_btn = QPushButton("Export Logs")
        export_btn.setProperty("class", "primary")
        export_btn.clicked.connect(self._export_logs)
        export_layout.addWidget(export_btn)

        report_btn = QPushButton("Generate Report")
        report_btn.setProperty("class", "primary")
        report_btn.clicked.connect(self._generate_report)
        export_layout.addWidget(report_btn)

        export_layout.addStretch()

        self.log_count_label = QLabel("Showing: 0 entries")
        export_layout.addWidget(self.log_count_label)

        layout.addLayout(export_layout)

    def update_logs(self, entries: list):
        """Update the logs display."""
        self._log_entries = entries
        self._refresh_table()

    def _refresh_table(self):
        """Refresh the logs table with current entries."""
        self.logs_table.setRowCount(len(self._log_entries))

        for row, entry in enumerate(self._log_entries):
            # Timestamp
            timestamp = entry.timestamp if isinstance(entry.timestamp, str) else entry.timestamp
            self.logs_table.setItem(row, 0, QTableWidgetItem(timestamp))

            # Level
            level = entry.level
            level_item = QTableWidgetItem(level)
            level_colors = {
                'DEBUG': '#888',
                'INFO': '#4CAF50',
                'WARNING': '#FF9800',
                'ERROR': '#f44336',
                'CRITICAL': '#9C27B0',
                'ALERT': '#f44336'
            }
            level_item.setForeground(QColor(level_colors.get(level, '#888')))
            self.logs_table.setItem(row, 1, level_item)

            # Category
            self.logs_table.setItem(row, 2, QTableWidgetItem(entry.category))

            # Message
            self.logs_table.setItem(row, 3, QTableWidgetItem(entry.message))

            # Details (truncated)
            details = ""
            if entry.source_ip:
                details += f"Source: {entry.source_ip} "
            if entry.dest_ip:
                details += f"Dest: {entry.dest_ip} "
            if entry.process_name:
                details += f"Process: {entry.process_name}"
            self.logs_table.setItem(row, 4, QTableWidgetItem(details.strip() or "-"))

            # Store entry reference
            self.logs_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, entry)

        self.log_count_label.setText(f"Showing: {len(self._log_entries)} entries")

    def _apply_filters(self):
        """Apply filters to the logs."""
        # Get filter values
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        severity = self.severity_filter.currentText()
        category = self.category_filter.currentText()
        search = self.search_input.text().lower()

        # Filter entries
        filtered = []
        for entry in self._log_entries:
            # Parse entry date
            try:
                entry_date = datetime.fromisoformat(entry.timestamp).date()
            except (ValueError, AttributeError):
                entry_date = datetime.now().date()

            # Apply date filter
            if entry_date < date_from or entry_date > date_to:
                continue

            # Apply severity filter
            if severity != "All" and entry.level != severity:
                continue

            # Apply category filter
            if category != "All" and entry.category != category:
                continue

            # Apply search filter
            if search:
                searchable = f"{entry.message} {entry.source_ip or ''} {entry.dest_ip or ''} {entry.process_name or ''}".lower()
                if search not in searchable:
                    continue

            filtered.append(entry)

        # Update table with filtered entries
        original = self._log_entries
        self._log_entries = filtered
        self._refresh_table()
        self._log_entries = original

    def _on_log_selected(self, row, col):
        """Handle log entry selection."""
        item = self.logs_table.item(row, 0)
        if item:
            entry = item.data(Qt.ItemDataRole.UserRole)
            if entry:
                self._show_log_details(entry)

    def _show_log_details(self, entry):
        """Show log entry details."""
        details = f"""
<h4>{entry.message}</h4>
<p><b>Timestamp:</b> {entry.timestamp}</p>
<p><b>Level:</b> {entry.level}</p>
<p><b>Category:</b> {entry.category}</p>
"""

        if entry.source_ip:
            details += f"<p><b>Source IP:</b> {entry.source_ip}</p>"
        if entry.dest_ip:
            details += f"<p><b>Destination IP:</b> {entry.dest_ip}</p>"
        if entry.process_name:
            details += f"<p><b>Process:</b> {entry.process_name}</p>"
        if entry.rule_id:
            details += f"<p><b>Rule ID:</b> {entry.rule_id}</p>"
        if entry.details:
            details += "<p><b>Additional Details:</b></p><pre>"
            import json
            details += json.dumps(entry.details, indent=2)
            details += "</pre>"

        self.log_details.setHtml(details)

    def _export_logs(self):
        """Export logs to file."""
        format_map = {
            "Text (.txt)": ("txt", "Text Files (*.txt)"),
            "JSON (.json)": ("json", "JSON Files (*.json)"),
            "CSV (.csv)": ("csv", "CSV Files (*.csv)"),
            "JSON Lines (.jsonl)": ("jsonl", "JSON Lines Files (*.jsonl)")
        }

        format_choice = self.export_format.currentText()
        ext, filter_str = format_map.get(format_choice, ("txt", "Text Files (*.txt)"))

        # Get save location
        default_name = f"firewall_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", default_name, filter_str
        )

        if filename:
            self.export_requested.emit(filename, ext)
            QMessageBox.information(self, "Export Complete", f"Logs exported to:\n{filename}")

    def _generate_report(self):
        """Generate a summary report."""
        default_name = f"firewall_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Report", default_name, "Text Files (*.txt)"
        )

        if filename:
            self.generate_report_requested.emit(filename)
            QMessageBox.information(self, "Report Generated", f"Report saved to:\n{filename}")

    def add_log_entry(self, entry):
        """Add a new log entry."""
        self._log_entries.insert(0, entry)

        # Keep only last 1000 entries in memory
        if len(self._log_entries) > 1000:
            self._log_entries = self._log_entries[:1000]

        self._refresh_table()
