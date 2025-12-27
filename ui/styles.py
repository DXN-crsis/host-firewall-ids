"""
Styles Module
Defines dark and light themes for the application using QSS (Qt Style Sheets).
"""


class Colors:
    """Color palette for the application."""

    # Dark theme colors
    DARK = {
        'primary': '#2196F3',       # Blue
        'primary_dark': '#1976D2',
        'primary_light': '#64B5F6',
        'secondary': '#FF9800',     # Orange
        'success': '#4CAF50',       # Green
        'warning': '#FF9800',       # Orange
        'danger': '#f44336',        # Red
        'info': '#2196F3',          # Blue

        'background': '#1a1a2e',
        'background_alt': '#16213e',
        'surface': '#0f3460',
        'surface_light': '#1a4a7a',

        'text': '#ffffff',
        'text_secondary': '#b0b0b0',
        'text_muted': '#707070',

        'border': '#3a3a5a',
        'border_light': '#4a4a6a',

        'hover': '#2a2a4e',
        'selected': '#3a3a6e',

        'scrollbar': '#3a3a5a',
        'scrollbar_hover': '#4a4a6a',
    }

    # Light theme colors
    LIGHT = {
        'primary': '#1976D2',
        'primary_dark': '#0D47A1',
        'primary_light': '#42A5F5',
        'secondary': '#FF9800',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'danger': '#f44336',
        'info': '#2196F3',

        'background': '#f5f5f5',
        'background_alt': '#ffffff',
        'surface': '#ffffff',
        'surface_light': '#fafafa',

        'text': '#212121',
        'text_secondary': '#616161',
        'text_muted': '#9e9e9e',

        'border': '#e0e0e0',
        'border_light': '#eeeeee',

        'hover': '#eeeeee',
        'selected': '#e3f2fd',

        'scrollbar': '#c0c0c0',
        'scrollbar_hover': '#a0a0a0',
    }


class Styles:
    """Application styles and themes."""

    @staticmethod
    def get_dark_theme() -> str:
        """Get dark theme QSS stylesheet."""
        c = Colors.DARK
        return f'''
        /* Main Window */
        QMainWindow {{
            background-color: {c['background']};
        }}

        QWidget {{
            background-color: {c['background']};
            color: {c['text']};
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 10pt;
        }}

        /* Labels */
        QLabel {{
            color: {c['text']};
            background-color: transparent;
        }}

        QLabel[class="title"] {{
            font-size: 18pt;
            font-weight: bold;
            color: {c['primary_light']};
        }}

        QLabel[class="subtitle"] {{
            font-size: 12pt;
            color: {c['text_secondary']};
        }}

        QLabel[class="stat-value"] {{
            font-size: 24pt;
            font-weight: bold;
            color: {c['primary']};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px 16px;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {c['surface_light']};
            border-color: {c['primary']};
        }}

        QPushButton:pressed {{
            background-color: {c['primary_dark']};
        }}

        QPushButton:disabled {{
            background-color: {c['background_alt']};
            color: {c['text_muted']};
        }}

        QPushButton[class="primary"] {{
            background-color: {c['primary']};
            border-color: {c['primary']};
        }}

        QPushButton[class="primary"]:hover {{
            background-color: {c['primary_dark']};
        }}

        QPushButton[class="danger"] {{
            background-color: {c['danger']};
            border-color: {c['danger']};
        }}

        QPushButton[class="danger"]:hover {{
            background-color: #c62828;
        }}

        QPushButton[class="success"] {{
            background-color: {c['success']};
            border-color: {c['success']};
        }}

        QPushButton[class="nav-button"] {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            min-width: 150px;
        }}

        QPushButton[class="nav-button"]:hover {{
            background-color: {c['hover']};
        }}

        QPushButton[class="nav-button"]:checked {{
            background-color: {c['selected']};
            border-left: 3px solid {c['primary']};
        }}

        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px;
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {c['primary']};
        }}

        QLineEdit:disabled {{
            background-color: {c['background_alt']};
            color: {c['text_muted']};
        }}

        /* ComboBox */
        QComboBox {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px;
            min-width: 100px;
        }}

        QComboBox:hover {{
            border-color: {c['primary']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {c['text']};
            margin-right: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            selection-background-color: {c['primary']};
        }}

        /* SpinBox */
        QSpinBox, QDoubleSpinBox {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px;
        }}

        /* CheckBox */
        QCheckBox {{
            color: {c['text']};
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {c['border']};
            border-radius: 4px;
            background-color: {c['surface']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {c['primary']};
            border-color: {c['primary']};
        }}

        QCheckBox::indicator:hover {{
            border-color: {c['primary']};
        }}

        /* Tables */
        QTableWidget, QTableView {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            gridline-color: {c['border']};
            selection-background-color: {c['selected']};
        }}

        QTableWidget::item, QTableView::item {{
            padding: 8px;
        }}

        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: {c['selected']};
        }}

        QHeaderView::section {{
            background-color: {c['background_alt']};
            color: {c['text']};
            padding: 10px;
            border: none;
            border-bottom: 2px solid {c['primary']};
            font-weight: bold;
        }}

        /* ScrollBars */
        QScrollBar:vertical {{
            background-color: {c['background']};
            width: 12px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background-color: {c['scrollbar']};
            border-radius: 6px;
            min-height: 30px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {c['scrollbar_hover']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QScrollBar:horizontal {{
            background-color: {c['background']};
            height: 12px;
            margin: 0;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {c['scrollbar']};
            border-radius: 6px;
            min-width: 30px;
            margin: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {c['scrollbar_hover']};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 10px;
        }}

        QTabBar::tab {{
            background-color: {c['background_alt']};
            color: {c['text']};
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {c['surface']};
            border-bottom: 2px solid {c['primary']};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {c['hover']};
        }}

        /* GroupBox */
        QGroupBox {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            margin-top: 16px;
            padding-top: 16px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 16px;
            padding: 0 8px;
            color: {c['primary_light']};
            font-weight: bold;
        }}

        /* Progress Bar */
        QProgressBar {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            text-align: center;
            color: {c['text']};
        }}

        QProgressBar::chunk {{
            background-color: {c['primary']};
            border-radius: 6px;
        }}

        /* Tooltips */
        QToolTip {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 6px;
        }}

        /* Menu */
        QMenu {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 24px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background-color: {c['selected']};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {c['border']};
            margin: 4px 8px;
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {c['border']};
        }}

        QSplitter::handle:horizontal {{
            width: 2px;
        }}

        QSplitter::handle:vertical {{
            height: 2px;
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {c['background_alt']};
            color: {c['text_secondary']};
            border-top: 1px solid {c['border']};
        }}

        /* Frame */
        QFrame[class="card"] {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            padding: 16px;
        }}

        QFrame[class="sidebar"] {{
            background-color: {c['background_alt']};
            border-right: 1px solid {c['border']};
        }}

        /* List Widget */
        QListWidget {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
        }}

        QListWidget::item {{
            padding: 10px;
            border-radius: 4px;
        }}

        QListWidget::item:selected {{
            background-color: {c['selected']};
        }}

        QListWidget::item:hover {{
            background-color: {c['hover']};
        }}
        '''

    @staticmethod
    def get_light_theme() -> str:
        """Get light theme QSS stylesheet."""
        c = Colors.LIGHT
        return f'''
        QMainWindow {{
            background-color: {c['background']};
        }}

        QWidget {{
            background-color: {c['background']};
            color: {c['text']};
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 10pt;
        }}

        QLabel {{
            color: {c['text']};
            background-color: transparent;
        }}

        QLabel[class="title"] {{
            font-size: 18pt;
            font-weight: bold;
            color: {c['primary']};
        }}

        QLabel[class="subtitle"] {{
            font-size: 12pt;
            color: {c['text_secondary']};
        }}

        QLabel[class="stat-value"] {{
            font-size: 24pt;
            font-weight: bold;
            color: {c['primary']};
        }}

        QPushButton {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px 16px;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {c['hover']};
            border-color: {c['primary']};
        }}

        QPushButton:pressed {{
            background-color: {c['selected']};
        }}

        QPushButton[class="primary"] {{
            background-color: {c['primary']};
            color: white;
            border-color: {c['primary']};
        }}

        QPushButton[class="primary"]:hover {{
            background-color: {c['primary_dark']};
        }}

        QPushButton[class="danger"] {{
            background-color: {c['danger']};
            color: white;
            border-color: {c['danger']};
        }}

        QPushButton[class="nav-button"] {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            min-width: 150px;
        }}

        QPushButton[class="nav-button"]:hover {{
            background-color: {c['hover']};
        }}

        QPushButton[class="nav-button"]:checked {{
            background-color: {c['selected']};
            border-left: 3px solid {c['primary']};
        }}

        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px;
        }}

        QLineEdit:focus {{
            border-color: {c['primary']};
        }}

        QComboBox {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px;
        }}

        QTableWidget, QTableView {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            gridline-color: {c['border']};
            selection-background-color: {c['selected']};
        }}

        QHeaderView::section {{
            background-color: {c['background']};
            color: {c['text']};
            padding: 10px;
            border: none;
            border-bottom: 2px solid {c['primary']};
            font-weight: bold;
        }}

        QScrollBar:vertical {{
            background-color: {c['background']};
            width: 12px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {c['scrollbar']};
            border-radius: 6px;
            min-height: 30px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {c['scrollbar_hover']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QFrame[class="card"] {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            padding: 16px;
        }}

        QFrame[class="sidebar"] {{
            background-color: {c['surface']};
            border-right: 1px solid {c['border']};
        }}

        QGroupBox {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            margin-top: 16px;
            padding-top: 16px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 16px;
            padding: 0 8px;
            color: {c['primary']};
            font-weight: bold;
        }}
        '''


def apply_theme(app, theme: str = 'dark'):
    """Apply a theme to the application."""
    if theme == 'dark':
        app.setStyleSheet(Styles.get_dark_theme())
    else:
        app.setStyleSheet(Styles.get_light_theme())
