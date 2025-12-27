"""
Styles Module
Defines glassmorphism dark/light themes for the application using QSS (Qt Style Sheets).
Beautiful black and white theme with smooth animations.
"""


class Colors:
    """Color palette for the application - Glassmorphism Black & White."""

    # Dark Glassmorphism theme colors (Black dominant)
    DARK = {
        'primary': '#ffffff',           # White accent
        'primary_dark': '#e0e0e0',
        'primary_light': '#ffffff',
        'secondary': '#808080',         # Gray
        'success': '#00ff88',           # Neon green
        'warning': '#ffaa00',           # Amber
        'danger': '#ff4466',            # Neon red
        'info': '#00aaff',              # Cyan

        'background': '#0a0a0f',        # Near black
        'background_alt': '#12121a',    # Dark charcoal
        'surface': 'rgba(20, 20, 30, 0.8)',  # Glass effect
        'surface_solid': '#14141e',     # Solid surface for tables
        'surface_light': 'rgba(30, 30, 45, 0.9)',

        'text': '#ffffff',
        'text_secondary': '#a0a0b0',
        'text_muted': '#606070',

        'border': 'rgba(255, 255, 255, 0.1)',
        'border_light': 'rgba(255, 255, 255, 0.15)',
        'border_glow': 'rgba(255, 255, 255, 0.3)',

        'hover': 'rgba(255, 255, 255, 0.1)',
        'selected': 'rgba(255, 255, 255, 0.15)',
        'pressed': 'rgba(255, 255, 255, 0.2)',

        'scrollbar': 'rgba(255, 255, 255, 0.2)',
        'scrollbar_hover': 'rgba(255, 255, 255, 0.35)',

        'glass': 'rgba(255, 255, 255, 0.05)',
        'glass_border': 'rgba(255, 255, 255, 0.1)',
        'shadow': 'rgba(0, 0, 0, 0.5)',

        'gradient_start': '#0a0a0f',
        'gradient_end': '#1a1a2e',
    }

    # Light Glassmorphism theme colors (White dominant)
    LIGHT = {
        'primary': '#1a1a1a',           # Dark accent
        'primary_dark': '#000000',
        'primary_light': '#333333',
        'secondary': '#666666',
        'success': '#00cc66',
        'warning': '#ff9900',
        'danger': '#ff3344',
        'info': '#0088cc',

        'background': '#f0f0f5',
        'background_alt': '#ffffff',
        'surface': 'rgba(255, 255, 255, 0.7)',
        'surface_solid': '#ffffff',
        'surface_light': 'rgba(255, 255, 255, 0.9)',

        'text': '#1a1a1a',
        'text_secondary': '#505060',
        'text_muted': '#909090',

        'border': 'rgba(0, 0, 0, 0.1)',
        'border_light': 'rgba(0, 0, 0, 0.08)',
        'border_glow': 'rgba(0, 0, 0, 0.2)',

        'hover': 'rgba(0, 0, 0, 0.05)',
        'selected': 'rgba(0, 0, 0, 0.08)',
        'pressed': 'rgba(0, 0, 0, 0.12)',

        'scrollbar': 'rgba(0, 0, 0, 0.15)',
        'scrollbar_hover': 'rgba(0, 0, 0, 0.25)',

        'glass': 'rgba(255, 255, 255, 0.6)',
        'glass_border': 'rgba(0, 0, 0, 0.1)',
        'shadow': 'rgba(0, 0, 0, 0.1)',

        'gradient_start': '#f0f0f5',
        'gradient_end': '#e0e0e8',
    }


class Styles:
    """Application styles and themes with Glassmorphism design."""

    @staticmethod
    def get_dark_theme() -> str:
        """Get dark glassmorphism theme QSS stylesheet."""
        c = Colors.DARK
        return f'''
        /* ==================== GLOBAL STYLES ==================== */

        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['gradient_start']}, stop:1 {c['gradient_end']});
        }}

        QWidget {{
            background-color: transparent;
            color: {c['text']};
            font-family: "Segoe UI", "SF Pro Display", "Arial", sans-serif;
            font-size: 10pt;
            selection-background-color: rgba(255, 255, 255, 0.2);
            selection-color: {c['text']};
        }}

        /* ==================== LABELS ==================== */

        QLabel {{
            color: {c['text']};
            background-color: transparent;
            padding: 2px;
        }}

        QLabel[class="title"] {{
            font-size: 20pt;
            font-weight: 600;
            color: {c['primary']};
            letter-spacing: 1px;
        }}

        QLabel[class="subtitle"] {{
            font-size: 12pt;
            font-weight: 400;
            color: {c['text_secondary']};
        }}

        QLabel[class="stat-value"] {{
            font-size: 28pt;
            font-weight: 700;
            color: {c['primary']};
        }}

        /* ==================== BUTTONS ==================== */

        QPushButton {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border_light']};
            border-radius: 8px;
            padding: 10px 20px;
            min-width: 80px;
            font-weight: 500;
        }}

        QPushButton:hover {{
            background-color: {c['hover']};
            border-color: {c['border_glow']};
        }}

        QPushButton:pressed {{
            background-color: {c['pressed']};
            border-color: {c['primary']};
        }}

        QPushButton:disabled {{
            background-color: rgba(20, 20, 30, 0.3);
            color: {c['text_muted']};
            border-color: transparent;
        }}

        QPushButton[class="primary"] {{
            background-color: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: {c['primary']};
            font-weight: 600;
        }}

        QPushButton[class="primary"]:hover {{
            background-color: rgba(255, 255, 255, 0.25);
            border-color: {c['primary']};
        }}

        QPushButton[class="primary"]:pressed {{
            background-color: rgba(255, 255, 255, 0.35);
        }}

        QPushButton[class="danger"] {{
            background-color: rgba(255, 68, 102, 0.2);
            border: 1px solid rgba(255, 68, 102, 0.4);
            color: {c['danger']};
        }}

        QPushButton[class="danger"]:hover {{
            background-color: rgba(255, 68, 102, 0.35);
            border-color: {c['danger']};
        }}

        QPushButton[class="success"] {{
            background-color: rgba(0, 255, 136, 0.15);
            border: 1px solid rgba(0, 255, 136, 0.3);
            color: {c['success']};
        }}

        QPushButton[class="success"]:hover {{
            background-color: rgba(0, 255, 136, 0.25);
            border-color: {c['success']};
        }}

        /* Navigation Buttons */
        QPushButton[class="nav-button"] {{
            background-color: transparent;
            border: none;
            border-radius: 10px;
            padding: 14px 20px;
            text-align: left;
            min-width: 160px;
            font-weight: 500;
            color: {c['text_secondary']};
        }}

        QPushButton[class="nav-button"]:hover {{
            background-color: {c['hover']};
            color: {c['text']};
        }}

        QPushButton[class="nav-button"]:checked {{
            background-color: rgba(255, 255, 255, 0.1);
            border-left: 3px solid {c['primary']};
            color: {c['primary']};
        }}

        /* ==================== INPUT FIELDS ==================== */

        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 10pt;
        }}

        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
            border-color: {c['border_light']};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {c['border_glow']};
            background-color: {c['surface_light']};
        }}

        QLineEdit:disabled {{
            background-color: rgba(20, 20, 30, 0.3);
            color: {c['text_muted']};
        }}

        QLineEdit::placeholder {{
            color: {c['text_muted']};
        }}

        /* ==================== COMBO BOX ==================== */

        QComboBox {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 10px 14px;
            min-width: 120px;
        }}

        QComboBox:hover {{
            border-color: {c['border_light']};
        }}

        QComboBox:focus {{
            border-color: {c['border_glow']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
            background: transparent;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {c['text_secondary']};
            margin-right: 10px;
        }}

        QComboBox::down-arrow:hover {{
            border-top-color: {c['text']};
        }}

        QComboBox QAbstractItemView {{
            background-color: {c['surface_solid']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            selection-background-color: rgba(255, 255, 255, 0.15);
            padding: 4px;
            outline: none;
        }}

        QComboBox QAbstractItemView::item {{
            padding: 10px;
            border-radius: 6px;
        }}

        QComboBox QAbstractItemView::item:hover {{
            background-color: {c['hover']};
        }}

        /* ==================== SPIN BOX ==================== */

        QSpinBox, QDoubleSpinBox {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 10px;
        }}

        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {c['border_light']};
        }}

        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            background-color: transparent;
            border: none;
            width: 20px;
        }}

        /* ==================== CHECK BOX ==================== */

        QCheckBox {{
            color: {c['text']};
            spacing: 10px;
        }}

        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {c['border_light']};
            border-radius: 6px;
            background-color: transparent;
        }}

        QCheckBox::indicator:hover {{
            border-color: {c['border_glow']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {c['primary']};
            border-color: {c['primary']};
        }}

        QCheckBox::indicator:checked:hover {{
            background-color: {c['primary_dark']};
        }}

        /* ==================== DATE EDIT ==================== */

        QDateEdit {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 10px;
        }}

        QDateEdit::drop-down {{
            border: none;
            width: 30px;
        }}

        QCalendarWidget {{
            background-color: {c['surface_solid']};
        }}

        /* ==================== TABLES ==================== */

        QTableWidget, QTableView {{
            background-color: {c['surface_solid']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            gridline-color: rgba(255, 255, 255, 0.05);
            selection-background-color: rgba(255, 255, 255, 0.1);
            outline: none;
        }}

        QTableWidget::item, QTableView::item {{
            padding: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }}

        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: rgba(255, 255, 255, 0.1);
        }}

        QTableWidget::item:hover, QTableView::item:hover {{
            background-color: rgba(255, 255, 255, 0.05);
        }}

        QHeaderView::section {{
            background-color: rgba(255, 255, 255, 0.03);
            color: {c['text_secondary']};
            padding: 12px 10px;
            border: none;
            border-bottom: 1px solid {c['border']};
            font-weight: 600;
            text-transform: uppercase;
            font-size: 9pt;
            letter-spacing: 0.5px;
        }}

        QHeaderView::section:hover {{
            background-color: rgba(255, 255, 255, 0.06);
            color: {c['text']};
        }}

        /* Corner button */
        QTableCornerButton::section {{
            background-color: rgba(255, 255, 255, 0.03);
            border: none;
        }}

        /* ==================== SCROLL BARS ==================== */

        QScrollBar:vertical {{
            background-color: transparent;
            width: 10px;
            margin: 4px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {c['scrollbar']};
            border-radius: 5px;
            min-height: 40px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {c['scrollbar_hover']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
            background: none;
        }}

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar:horizontal {{
            background-color: transparent;
            height: 10px;
            margin: 4px;
            border-radius: 5px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {c['scrollbar']};
            border-radius: 5px;
            min-width: 40px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {c['scrollbar_hover']};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
            background: none;
        }}

        /* ==================== TAB WIDGET ==================== */

        QTabWidget::pane {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            padding: 16px;
            margin-top: -1px;
        }}

        QTabBar::tab {{
            background-color: transparent;
            color: {c['text_secondary']};
            padding: 12px 24px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            margin-right: 4px;
            font-weight: 500;
        }}

        QTabBar::tab:selected {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-bottom: none;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {c['hover']};
            color: {c['text']};
        }}

        /* ==================== GROUP BOX ==================== */

        QGroupBox {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            margin-top: 20px;
            padding: 20px;
            padding-top: 30px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 20px;
            top: 8px;
            padding: 0 10px;
            color: {c['text']};
            font-weight: 600;
            font-size: 10pt;
            background-color: {c['surface_solid']};
            border-radius: 4px;
        }}

        /* ==================== PROGRESS BAR ==================== */

        QProgressBar {{
            background-color: rgba(255, 255, 255, 0.05);
            border: none;
            border-radius: 6px;
            text-align: center;
            color: {c['text']};
            height: 12px;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.3), stop:1 rgba(255, 255, 255, 0.5));
            border-radius: 6px;
        }}

        /* ==================== TOOLTIPS ==================== */

        QToolTip {{
            background-color: {c['surface_solid']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 9pt;
        }}

        /* ==================== MENU ==================== */

        QMenu {{
            background-color: {c['surface_solid']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 10px;
            padding: 6px;
        }}

        QMenu::item {{
            padding: 10px 30px 10px 20px;
            border-radius: 6px;
            margin: 2px;
        }}

        QMenu::item:selected {{
            background-color: {c['hover']};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {c['border']};
            margin: 6px 12px;
        }}

        QMenu::indicator {{
            width: 16px;
            height: 16px;
            margin-left: 6px;
        }}

        /* ==================== SPLITTER ==================== */

        QSplitter::handle {{
            background-color: transparent;
        }}

        QSplitter::handle:horizontal {{
            width: 6px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent, stop:0.4 {c['border']},
                stop:0.6 {c['border']}, stop:1 transparent);
        }}

        QSplitter::handle:vertical {{
            height: 6px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 transparent, stop:0.4 {c['border']},
                stop:0.6 {c['border']}, stop:1 transparent);
        }}

        QSplitter::handle:hover {{
            background-color: {c['border_light']};
        }}

        /* ==================== STATUS BAR ==================== */

        QStatusBar {{
            background-color: rgba(10, 10, 15, 0.9);
            color: {c['text_secondary']};
            border-top: 1px solid {c['border']};
            padding: 6px;
        }}

        QStatusBar::item {{
            border: none;
        }}

        /* ==================== FRAMES ==================== */

        QFrame[class="card"] {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 16px;
            padding: 20px;
        }}

        QFrame[class="card"]:hover {{
            border-color: {c['border_light']};
        }}

        QFrame[class="sidebar"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(18, 18, 26, 0.95), stop:1 rgba(10, 10, 15, 0.98));
            border-right: 1px solid {c['border']};
        }}

        QFrame[class="glass"] {{
            background-color: {c['glass']};
            border: 1px solid {c['glass_border']};
            border-radius: 16px;
        }}

        /* ==================== LIST WIDGET ==================== */

        QListWidget {{
            background-color: {c['surface_solid']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 10px;
            outline: none;
        }}

        QListWidget::item {{
            padding: 12px 16px;
            border-radius: 6px;
            margin: 2px 4px;
        }}

        QListWidget::item:selected {{
            background-color: rgba(255, 255, 255, 0.1);
        }}

        QListWidget::item:hover {{
            background-color: {c['hover']};
        }}

        /* ==================== MESSAGE BOX ==================== */

        QMessageBox {{
            background-color: {c['surface_solid']};
        }}

        QMessageBox QLabel {{
            color: {c['text']};
            font-size: 10pt;
        }}

        QMessageBox QPushButton {{
            min-width: 100px;
        }}

        /* ==================== DIALOG ==================== */

        QDialog {{
            background-color: {c['surface_solid']};
            border-radius: 16px;
        }}

        QDialogButtonBox {{
            button-layout: 2;
        }}

        /* ==================== FILE DIALOG ==================== */

        QFileDialog {{
            background-color: {c['surface_solid']};
        }}

        /* ==================== SLIDER ==================== */

        QSlider::groove:horizontal {{
            background-color: rgba(255, 255, 255, 0.1);
            height: 6px;
            border-radius: 3px;
        }}

        QSlider::handle:horizontal {{
            background-color: {c['primary']};
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}

        QSlider::handle:horizontal:hover {{
            background-color: {c['primary_dark']};
        }}

        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.2), stop:1 rgba(255, 255, 255, 0.4));
            border-radius: 3px;
        }}
        '''

    @staticmethod
    def get_light_theme() -> str:
        """Get light glassmorphism theme QSS stylesheet."""
        c = Colors.LIGHT
        return f'''
        /* ==================== GLOBAL STYLES ==================== */

        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['gradient_start']}, stop:1 {c['gradient_end']});
        }}

        QWidget {{
            background-color: transparent;
            color: {c['text']};
            font-family: "Segoe UI", "SF Pro Display", "Arial", sans-serif;
            font-size: 10pt;
            selection-background-color: rgba(0, 0, 0, 0.1);
            selection-color: {c['text']};
        }}

        /* ==================== LABELS ==================== */

        QLabel {{
            color: {c['text']};
            background-color: transparent;
            padding: 2px;
        }}

        QLabel[class="title"] {{
            font-size: 20pt;
            font-weight: 600;
            color: {c['primary']};
            letter-spacing: 1px;
        }}

        QLabel[class="subtitle"] {{
            font-size: 12pt;
            font-weight: 400;
            color: {c['text_secondary']};
        }}

        QLabel[class="stat-value"] {{
            font-size: 28pt;
            font-weight: 700;
            color: {c['primary']};
        }}

        /* ==================== BUTTONS ==================== */

        QPushButton {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 10px 20px;
            min-width: 80px;
            font-weight: 500;
        }}

        QPushButton:hover {{
            background-color: rgba(0, 0, 0, 0.05);
            border-color: {c['border_glow']};
        }}

        QPushButton:pressed {{
            background-color: {c['pressed']};
        }}

        QPushButton:disabled {{
            background-color: rgba(200, 200, 200, 0.3);
            color: {c['text_muted']};
            border-color: transparent;
        }}

        QPushButton[class="primary"] {{
            background-color: rgba(0, 0, 0, 0.8);
            border: 1px solid {c['primary']};
            color: white;
            font-weight: 600;
        }}

        QPushButton[class="primary"]:hover {{
            background-color: rgba(0, 0, 0, 0.9);
        }}

        QPushButton[class="danger"] {{
            background-color: rgba(255, 51, 68, 0.15);
            border: 1px solid rgba(255, 51, 68, 0.4);
            color: {c['danger']};
        }}

        QPushButton[class="danger"]:hover {{
            background-color: rgba(255, 51, 68, 0.25);
        }}

        QPushButton[class="success"] {{
            background-color: rgba(0, 204, 102, 0.15);
            border: 1px solid rgba(0, 204, 102, 0.4);
            color: {c['success']};
        }}

        /* Navigation Buttons */
        QPushButton[class="nav-button"] {{
            background-color: transparent;
            border: none;
            border-radius: 10px;
            padding: 14px 20px;
            text-align: left;
            min-width: 160px;
            font-weight: 500;
            color: {c['text_secondary']};
        }}

        QPushButton[class="nav-button"]:hover {{
            background-color: {c['hover']};
            color: {c['text']};
        }}

        QPushButton[class="nav-button"]:checked {{
            background-color: rgba(0, 0, 0, 0.08);
            border-left: 3px solid {c['primary']};
            color: {c['primary']};
        }}

        /* ==================== INPUT FIELDS ==================== */

        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 10px 14px;
        }}

        QLineEdit:hover, QTextEdit:hover {{
            border-color: {c['border_glow']};
        }}

        QLineEdit:focus, QTextEdit:focus {{
            border-color: {c['primary']};
            background-color: {c['surface_light']};
        }}

        /* ==================== COMBO BOX ==================== */

        QComboBox {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 10px 14px;
            min-width: 120px;
        }}

        QComboBox:hover {{
            border-color: {c['border_glow']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox::down-arrow {{
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {c['text_secondary']};
            margin-right: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {c['surface_solid']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            selection-background-color: {c['selected']};
        }}

        /* ==================== TABLES ==================== */

        QTableWidget, QTableView {{
            background-color: {c['surface_solid']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            gridline-color: {c['border_light']};
            selection-background-color: {c['selected']};
            outline: none;
        }}

        QTableWidget::item, QTableView::item {{
            padding: 10px;
            border-bottom: 1px solid {c['border_light']};
        }}

        QTableWidget::item:selected {{
            background-color: {c['selected']};
        }}

        QHeaderView::section {{
            background-color: rgba(0, 0, 0, 0.02);
            color: {c['text_secondary']};
            padding: 12px 10px;
            border: none;
            border-bottom: 1px solid {c['border']};
            font-weight: 600;
            text-transform: uppercase;
            font-size: 9pt;
        }}

        /* ==================== SCROLL BARS ==================== */

        QScrollBar:vertical {{
            background-color: transparent;
            width: 10px;
            margin: 4px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {c['scrollbar']};
            border-radius: 5px;
            min-height: 40px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {c['scrollbar_hover']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        /* ==================== TAB WIDGET ==================== */

        QTabWidget::pane {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            padding: 16px;
        }}

        QTabBar::tab {{
            background-color: transparent;
            color: {c['text_secondary']};
            padding: 12px 24px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            margin-right: 4px;
            font-weight: 500;
        }}

        QTabBar::tab:selected {{
            background-color: {c['surface']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-bottom: none;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {c['hover']};
        }}

        /* ==================== GROUP BOX ==================== */

        QGroupBox {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            margin-top: 20px;
            padding: 20px;
            padding-top: 30px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 20px;
            top: 8px;
            padding: 0 10px;
            color: {c['text']};
            font-weight: 600;
            background-color: {c['surface_solid']};
            border-radius: 4px;
        }}

        /* ==================== FRAMES ==================== */

        QFrame[class="card"] {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 16px;
            padding: 20px;
        }}

        QFrame[class="sidebar"] {{
            background-color: {c['surface_solid']};
            border-right: 1px solid {c['border']};
        }}

        /* ==================== LIST WIDGET ==================== */

        QListWidget {{
            background-color: {c['surface_solid']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 10px;
        }}

        QListWidget::item {{
            padding: 12px 16px;
            border-radius: 6px;
            margin: 2px 4px;
        }}

        QListWidget::item:selected {{
            background-color: {c['selected']};
        }}

        QListWidget::item:hover {{
            background-color: {c['hover']};
        }}

        /* ==================== PROGRESS BAR ==================== */

        QProgressBar {{
            background-color: rgba(0, 0, 0, 0.05);
            border: none;
            border-radius: 6px;
            height: 12px;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 0, 0, 0.5), stop:1 rgba(0, 0, 0, 0.8));
            border-radius: 6px;
        }}

        /* ==================== TOOLTIPS ==================== */

        QToolTip {{
            background-color: {c['surface_solid']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 8px 12px;
        }}

        /* ==================== MENU ==================== */

        QMenu {{
            background-color: {c['surface_solid']};
            border: 1px solid {c['border']};
            border-radius: 10px;
            padding: 6px;
        }}

        QMenu::item {{
            padding: 10px 30px 10px 20px;
            border-radius: 6px;
            margin: 2px;
        }}

        QMenu::item:selected {{
            background-color: {c['hover']};
        }}

        /* ==================== DIALOG ==================== */

        QDialog {{
            background-color: {c['surface_solid']};
        }}

        QMessageBox {{
            background-color: {c['surface_solid']};
        }}

        /* ==================== CHECK BOX ==================== */

        QCheckBox {{
            color: {c['text']};
            spacing: 10px;
        }}

        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {c['border']};
            border-radius: 6px;
            background-color: transparent;
        }}

        QCheckBox::indicator:checked {{
            background-color: {c['primary']};
            border-color: {c['primary']};
        }}

        /* ==================== STATUS BAR ==================== */

        QStatusBar {{
            background-color: rgba(255, 255, 255, 0.9);
            border-top: 1px solid {c['border']};
            padding: 6px;
        }}
        '''


def apply_theme(app, theme: str = 'dark'):
    """Apply a theme to the application."""
    if theme == 'dark':
        app.setStyleSheet(Styles.get_dark_theme())
    else:
        app.setStyleSheet(Styles.get_light_theme())


def get_animation_duration() -> int:
    """Get the standard animation duration in milliseconds."""
    return 200


def get_hover_animation_duration() -> int:
    """Get hover animation duration in milliseconds."""
    return 150
