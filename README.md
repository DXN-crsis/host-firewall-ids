# SaadFirewall - Smart Host Firewall + Intrusion Detection System

<div align="center">

**A Defensive Security Tool for Windows**

![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![License](https://img.shields.io/badge/License-Educational-orange)

</div>

---

## Overview

SaadFirewall is a comprehensive defensive security application designed to protect Windows systems from network intrusion attempts. It combines real-time network monitoring, rule-based intrusion detection, and Windows Firewall management in a modern, user-friendly interface.

### Key Features

- **Real-time Network Monitoring**: Track all active TCP/UDP connections with process information
- **Intrusion Detection Engine**: Detect suspicious patterns like beaconing, port scanning, and brute force attempts
- **Windows Firewall Integration**: Block/unblock IPs and ports directly through the application
- **Security Alerts**: Get notified of threats with recommended actions
- **Comprehensive Logging**: JSONL + text logs with export and reporting capabilities
- **Modern UI**: Professional dark/light theme with intuitive navigation

---

## Screenshots

The application features a professional dashboard interface suitable for demonstrations:

```
┌─────────────────────────────────────────────────────────────────┐
│  SaadFirewall                                                   │
├─────────────┬───────────────────────────────────────────────────┤
│             │  Network Dashboard                                │
│ 📊 Dashboard│  ┌────────┬────────┬────────┬────────┐           │
│ 🛡️ Rules    │  │ Total  │Establ. │Unique  │ Alerts │           │
│ ⚠️ Alerts   │  │  42    │  28    │   15   │   2    │           │
│ 📋 Logs     │  └────────┴────────┴────────┴────────┘           │
│ ⚙️ Settings │                                                   │
│ ℹ️ About    │  [Connection Table with Process Info]            │
│             │                                                   │
│             │  Top Remote IPs    |  Top Ports                  │
│ [Monitoring]│  192.168.1.1   12  |  443      28                │
│ [Start/Stop]│  8.8.8.8        8  |  80       15                │
└─────────────┴───────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- Windows 10/11
- Python 3.10 or higher
- Administrator privileges (for firewall operations)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-repo/Fire-wall.git
cd Fire-wall
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Windows-specific Package (Optional)

For Windows Event Log monitoring:

```bash
pip install pywin32
```

### Step 5: Run the Application

```bash
python main.py
```

**Note**: For full functionality (firewall operations, event log reading), run as Administrator:
- Right-click Command Prompt → "Run as administrator"
- Navigate to the project folder and run `python main.py`

---

## Usage Guide

### Dashboard

The main dashboard displays:
- **Statistics Cards**: Total connections, established connections, unique remote IPs, active alerts
- **Connection Table**: Real-time view of all network connections with:
  - Local/Remote IP and Port
  - Protocol (TCP/UDP)
  - Connection Status
  - Process Name and PID
  - Risk Level indicator
- **Top Lists**: Most active remote IPs, ports, and processes

**Actions from Dashboard**:
- Double-click a connection to view details
- Right-click on a connection to block the IP
- Use the search bar to filter connections

### Firewall Rules

The Rules page allows you to:
- View all firewall rules created by the application
- Add new blocking rules for IPs or ports
- Enable/disable existing rules
- Delete rules
- Configure detection rule thresholds
- Manage threat intelligence lists (bad IPs/ports)

**Blocking an IP**:
1. Go to Rules → Add Rules tab
2. Enter the IP address
3. Select direction (Inbound/Outbound/Both)
4. Click "Block IP"

### Alerts

Security alerts are generated when:
- A process connects to many unique IPs (beaconing detection)
- Connections to suspicious ports are detected
- An IP connects to many of your ports (port scan)
- Multiple failed login attempts occur (from Event Log)

**Alert Actions**:
- **Acknowledge**: Mark alert as reviewed
- **Block**: Add the source/destination IP to firewall blocklist
- **View Details**: See full alert information

### Logs

The Logs page provides:
- Filterable log viewer (by date, severity, category)
- Search functionality
- Export to multiple formats (TXT, JSON, CSV, JSONL)
- Report generation

### Settings

Configure:
- Application behavior (start minimized, tray icon)
- Monitoring intervals
- Detection thresholds
- Appearance (dark/light theme)
- Logging options

---

## Demo Scenarios

### Scenario 1: Block a Suspicious IP

**Goal**: Demonstrate blocking an IP from the dashboard

1. Start the application as Administrator
2. Navigate to Dashboard
3. Wait for connections to appear in the table
4. Right-click on any remote IP
5. Select "Block IP: x.x.x.x"
6. Confirm the action
7. Verify:
   - Check Windows Firewall (wf.msc) → Inbound/Outbound Rules
   - Look for rules starting with "SaadFirewall_"
   - Go to Rules page in the app to see the rule

### Scenario 2: Trigger an Alert

**Goal**: Demonstrate the intrusion detection system

1. Start the application
2. Open multiple browser tabs quickly (to generate many connections)
3. Or run this PowerShell script to simulate connections:

```powershell
# Safe simulation - just creates TCP connections to common sites
1..25 | ForEach-Object {
    $tcp = New-Object System.Net.Sockets.TcpClient
    try { $tcp.ConnectAsync("google.com", 80) } catch {}
    Start-Sleep -Milliseconds 100
}
```

4. Watch the Alerts page for:
   - "High Connection Rate" alert
   - "Possible Beaconing" alert (if many unique IPs)
5. Click on the alert to see details
6. Try the "Block" action

### Scenario 3: Export Logs and Generate Report

**Goal**: Demonstrate logging capabilities

1. Run the application for a few minutes
2. Navigate to Logs page
3. Apply filters:
   - Set date range
   - Select severity level
   - Search for specific IP
4. Click "Export Logs"
5. Choose format (TXT, JSON, CSV)
6. Save the file
7. Click "Generate Report"
8. Open the generated report to show statistics

### Scenario 4: Configure Detection Rules

**Goal**: Show customization of detection settings

1. Go to Rules page
2. Click "Detection Settings" tab
3. Demonstrate:
   - Enabling/disabling specific rules
   - Adjusting thresholds
   - Adding custom bad ports
   - Adding threat intelligence IPs
4. Save settings
5. Show how settings affect detection

---

## PowerShell Commands Reference

The application uses these PowerShell commands for firewall management:

```powershell
# Block an IP (Inbound)
New-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100_In" `
    -Direction Inbound -Action Block -RemoteAddress "192.168.1.100"

# Block an IP (Outbound)
New-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100_Out" `
    -Direction Outbound -Action Block -RemoteAddress "192.168.1.100"

# Block a Port
New-NetFirewallRule -DisplayName "SaadFirewall_Block_Port_4444_TCP_In" `
    -Direction Inbound -Action Block -LocalPort 4444 -Protocol TCP

# List all our rules
Get-NetFirewallRule -DisplayName "SaadFirewall_*"

# Remove a specific rule
Remove-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100_In"

# Enable/Disable a rule
Enable-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100_In"
Disable-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100_In"

# Remove all our rules (cleanup)
Remove-NetFirewallRule -DisplayName "SaadFirewall_*"

# Check firewall status
Get-NetFirewallProfile | Select-Object Name, Enabled
```

---

## Packaging to EXE

### Using PyInstaller

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Create the executable:

```bash
pyinstaller --name SaadFirewall ^
    --onefile ^
    --windowed ^
    --icon=resources/icons/app.ico ^
    --add-data "config.json;." ^
    --hidden-import=PyQt6 ^
    --hidden-import=psutil ^
    main.py
```

3. The executable will be in the `dist` folder.

### Build Script

Create `build.bat`:

```batch
@echo off
echo Building SaadFirewall...

REM Activate virtual environment
call venv\Scripts\activate

REM Clean previous builds
rmdir /s /q build dist 2>nul

REM Build
pyinstaller --name SaadFirewall ^
    --onefile ^
    --windowed ^
    --add-data "config.json;." ^
    --hidden-import=PyQt6 ^
    --hidden-import=psutil ^
    main.py

echo.
echo Build complete! Check the dist folder.
pause
```

### Notes on Packaging

- The EXE must be run as Administrator for full functionality
- Include `config.json` in the same directory as the EXE
- Create `logs` and `data` folders next to the EXE (or let the app create them)

---

## Project Structure

```
Fire-wall/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── config.json               # Default configuration
├── README.md                 # This file
├── ARCHITECTURE.md           # Technical documentation
│
├── core/                     # Core business logic
│   ├── __init__.py
│   ├── network_monitor.py    # Network connection monitoring
│   ├── rule_engine.py        # Intrusion detection rules
│   ├── firewall_manager.py   # Windows Firewall integration
│   └── event_monitor.py      # Windows Event Log monitoring
│
├── ui/                       # PyQt6 GUI components
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   ├── dashboard.py          # Dashboard page
│   ├── rules_page.py         # Firewall rules management
│   ├── alerts_page.py        # Security alerts view
│   ├── logs_page.py          # Log browser
│   ├── settings_page.py      # Settings page
│   ├── about_page.py         # About page
│   ├── styles.py             # Theme definitions
│   └── widgets.py            # Custom reusable widgets
│
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── logger.py             # Logging system
│   ├── config.py             # Configuration management
│   ├── database.py           # SQLite operations
│   └── helpers.py            # Helper functions
│
├── resources/                # Static resources
│   └── icons/                # Application icons
│
├── logs/                     # Log files (created at runtime)
└── data/                     # Data files (created at runtime)
```

---

## Detection Rules

| ID | Name | Description | Default Threshold |
|-----|------|-------------|-------------------|
| R001 | Beaconing Detection | Many unique IPs from one process | 20 IPs in 60 sec |
| R002 | Suspicious Port Access | Connections to bad ports | Any connection |
| R003 | High Connection Rate | Excessive connections from process | 50 connections |
| R004 | Failed Login Attempts | From Windows Event Log | 5 in 10 min |
| R005 | Known Bad IP | IP in threat list | Any connection |
| R006 | Port Scan Detection | One IP connecting to many ports | 10 ports in 30 sec |

---

## Troubleshooting

### "Admin Required" Message
- The application needs Administrator privileges for firewall operations
- Right-click → Run as administrator

### Firewall Rules Not Working
- Verify Windows Firewall is enabled: `Get-NetFirewallProfile`
- Check if rules exist: `Get-NetFirewallRule -DisplayName "SaadFirewall_*"`
- Try running PowerShell as Administrator and manually testing commands

### Event Log Not Working
- Install pywin32: `pip install pywin32`
- Must run as Administrator to read Security log
- Verify Event Log service is running

### High CPU Usage
- Increase poll interval in Settings
- Reduce the number of tracked connections

---

## Arabic Summary (ملخص بالعربية)

### نظرة عامة

برنامج **SaadFirewall** هو أداة أمنية دفاعية مصممة لحماية أنظمة ويندوز من محاولات الاختراق عبر الشبكة.

### الميزات الرئيسية

1. **مراقبة الشبكة في الوقت الفعلي**
   - عرض جميع الاتصالات النشطة
   - تتبع العمليات المسؤولة عن كل اتصال
   - إحصائيات مباشرة

2. **كشف التسلل**
   - اكتشاف أنماط مشبوهة مثل:
     - الاتصال بالعديد من العناوين (Beaconing)
     - فحص المنافذ (Port Scanning)
     - محاولات تسجيل الدخول الفاشلة
   - تنبيهات فورية مع توصيات

3. **التحكم في جدار الحماية**
   - حظر عناوين IP مباشرة من التطبيق
   - إدارة قواعد جدار الحماية
   - دعم الحظر المؤقت والدائم

4. **السجلات والتقارير**
   - تسجيل شامل لجميع الأحداث
   - تصدير بتنسيقات متعددة
   - إنشاء تقارير ملخصة

### متطلبات التشغيل

- ويندوز 10 أو 11
- بايثون 3.10 أو أحدث
- صلاحيات المسؤول (للتحكم في جدار الحماية)

### كيفية التشغيل

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل البرنامج
python main.py
```

### نصائح للعرض التقديمي

1. **شرح الهدف**: أداة دفاعية لحماية الأنظمة
2. **عرض الواجهة**: شرح كل صفحة ووظيفتها
3. **تنفيذ سيناريو عملي**: حظر IP وعرض النتيجة
4. **شرح الكود**: عرض الهيكلية والوحدات الرئيسية
5. **الإجابة على الأسئلة**: استعد لأسئلة عن الأمن والتقنيات المستخدمة

---

## License

This project is developed for educational purposes as part of a graduation project.

## Credits

- **Developer**: Graduation Project Team
- **Framework**: PyQt6
- **Network Monitoring**: psutil
- **Firewall Integration**: Windows PowerShell

---

*SaadFirewall - Protecting Windows Systems from Network Threats*
