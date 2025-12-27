"""
UI modules for Smart Host Firewall + IDS
Contains: Main Window, Dashboard, Rules, Alerts, Logs, Settings, About
"""

from .main_window import MainWindow
from .styles import Styles, apply_theme

__all__ = [
    'MainWindow',
    'Styles',
    'apply_theme'
]
