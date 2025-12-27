"""
About Page
Application information and credits.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AboutPage(QWidget):
    """
    About page with application information.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the about page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo/Title section
        title_frame = QFrame()
        title_frame.setProperty("class", "card")
        title_layout = QVBoxLayout(title_frame)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # App name
        app_name = QLabel("SaadFirewall")
        app_name.setStyleSheet("font-size: 32pt; font-weight: bold; color: #2196F3;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(app_name)

        # Subtitle
        subtitle = QLabel("Smart Host Firewall + Intrusion Detection System")
        subtitle.setStyleSheet("font-size: 14pt; color: #888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)

        # Version
        version = QLabel("Version 1.0.0")
        version.setStyleSheet("font-size: 11pt; color: #666;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(version)

        layout.addWidget(title_frame)

        # Description
        desc_group = QGroupBox("About")
        desc_layout = QVBoxLayout(desc_group)

        description = QLabel("""
SaadFirewall is a defensive security tool designed to protect Windows systems
from network intrusion attempts. It provides real-time network monitoring,
rule-based intrusion detection, and Windows Firewall integration.

Key Features:
- Real-time network connection monitoring
- Rule-based intrusion detection engine
- Windows Firewall management
- Security alerts with recommended actions
- Comprehensive logging and reporting
- Modern, user-friendly interface
        """)
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 11pt; line-height: 1.5;")
        desc_layout.addWidget(description)

        layout.addWidget(desc_group)

        # Technical info
        tech_group = QGroupBox("Technical Information")
        tech_layout = QVBoxLayout(tech_group)

        tech_info = QLabel("""
<b>Platform:</b> Windows 10/11<br>
<b>Python Version:</b> 3.10+<br>
<b>GUI Framework:</b> PyQt6<br>
<b>Network Monitoring:</b> psutil<br>
<b>Firewall Integration:</b> PowerShell/netsh<br>
<b>Database:</b> SQLite<br>
        """)
        tech_info.setTextFormat(Qt.TextFormat.RichText)
        tech_info.setStyleSheet("font-size: 11pt;")
        tech_layout.addWidget(tech_info)

        layout.addWidget(tech_group)

        # Credits
        credits_group = QGroupBox("Credits & Acknowledgments")
        credits_layout = QVBoxLayout(credits_group)

        credits = QLabel("""
<b>Developer:</b> Graduation Project Team<br>
<b>Supervisor:</b> [Supervisor Name]<br>
<b>Institution:</b> [Institution Name]<br>
<b>Year:</b> 2024<br><br>
<b>Open Source Libraries Used:</b><br>
- PyQt6 - Qt bindings for Python<br>
- psutil - Cross-platform process and system utilities<br>
- pywin32 - Python extensions for Windows<br>
        """)
        credits.setTextFormat(Qt.TextFormat.RichText)
        credits.setStyleSheet("font-size: 11pt;")
        credits.setWordWrap(True)
        credits_layout.addWidget(credits)

        layout.addWidget(credits_group)

        # Arabic section
        arabic_group = QGroupBox("نبذة عن البرنامج (Arabic)")
        arabic_layout = QVBoxLayout(arabic_group)

        arabic_text = QLabel("""
<div style="text-align: right; direction: rtl;">
<b>جدار الحماية الذكي + نظام كشف التسلل</b><br><br>
هذا التطبيق هو أداة أمنية دفاعية مصممة لحماية أنظمة ويندوز من محاولات اختراق الشبكة.<br><br>
<b>الميزات الرئيسية:</b><br>
• مراقبة اتصالات الشبكة في الوقت الفعلي<br>
• محرك كشف التسلل القائم على القواعد<br>
• التحكم في جدار حماية ويندوز<br>
• تنبيهات أمنية مع إجراءات موصى بها<br>
• تسجيل وتقارير شاملة<br>
• واجهة مستخدم حديثة وسهلة الاستخدام<br>
</div>
        """)
        arabic_text.setTextFormat(Qt.TextFormat.RichText)
        arabic_text.setStyleSheet("font-size: 11pt;")
        arabic_text.setWordWrap(True)
        arabic_layout.addWidget(arabic_text)

        layout.addWidget(arabic_group)

        # Disclaimer
        disclaimer = QLabel("""
<b>Disclaimer:</b> This software is provided for educational and defensive security purposes only.
The developers are not responsible for any misuse of this software.
        """)
        disclaimer.setTextFormat(Qt.TextFormat.RichText)
        disclaimer.setStyleSheet("font-size: 9pt; color: #888;")
        disclaimer.setWordWrap(True)
        disclaimer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(disclaimer)

        layout.addStretch()
