# Smart Host Firewall + Intrusion Detection System
## Architecture Documentation

---

## 1. System Overview

This application is a **defensive security tool** designed to protect Windows systems from network intrusion attempts. It combines:
- Real-time network connection monitoring
- Rule-based intrusion detection
- Windows Firewall integration
- Comprehensive logging and alerting

### Target Environment
- Windows 10/11
- Python 3.10+
- Requires Administrator privileges for firewall operations

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE (PyQt6)                         │
├─────────────┬──────────────┬──────────────┬────────────┬──────────┬─────────┤
│  Dashboard  │ Rules Manager│   Alerts     │    Logs    │ Settings │  About  │
└──────┬──────┴──────┬───────┴──────┬───────┴─────┬──────┴────┬─────┴─────────┘
       │             │              │             │           │
       ▼             ▼              ▼             ▼           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                                  │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│ Network Monitor │   Rule Engine   │ Firewall Manager│   Event Log Monitor   │
│   (psutil)      │ (Pattern Match) │  (PowerShell)   │     (pywin32)         │
└────────┬────────┴────────┬────────┴────────┬────────┴───────────┬───────────┘
         │                 │                 │                    │
         ▼                 ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
├──────────────────┬──────────────────┬───────────────────────────────────────┤
│   Config Manager │     Logger       │         Alert Storage                 │
│    (JSON)        │  (JSONL + TXT)   │          (SQLite)                     │
└──────────────────┴──────────────────┴───────────────────────────────────────┘
         │                 │                    │
         ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STORAGE (Local Files)                                │
│  config.json  │  logs/app.log  │  logs/events.jsonl  │  data/alerts.db      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Module Responsibilities

### 3.1 Core Modules (`core/`)

| Module | File | Responsibility |
|--------|------|----------------|
| **Network Monitor** | `network_monitor.py` | Enumerates active TCP/UDP connections using `psutil`, maps PIDs to process names, emits connection data to UI |
| **Rule Engine** | `rule_engine.py` | Analyzes connection patterns, detects anomalies (beaconing, port scanning, brute force), generates alerts |
| **Firewall Manager** | `firewall_manager.py` | Creates/deletes Windows Firewall rules via PowerShell, manages rule lifecycle |
| **Event Log Monitor** | `event_monitor.py` | Reads Windows Security Event Log for failed logins (Event ID 4625), requires admin privileges |

### 3.2 Utility Modules (`utils/`)

| Module | File | Responsibility |
|--------|------|----------------|
| **Logger** | `logger.py` | Centralized logging to JSONL + human-readable text files |
| **Config** | `config.py` | Load/save application settings (JSON format) |
| **Helpers** | `helpers.py` | Utility functions: admin check, IP validation, time formatting |
| **Database** | `database.py` | SQLite operations for alerts and connection history |

### 3.3 UI Modules (`ui/`)

| Module | File | Responsibility |
|--------|------|----------------|
| **Main Window** | `main_window.py` | Application shell with navigation sidebar |
| **Dashboard** | `dashboard.py` | Real-time connection table, statistics, risk indicators |
| **Rules Manager** | `rules_page.py` | List/create/delete firewall rules |
| **Alerts View** | `alerts_page.py` | Display security alerts with actions |
| **Logs View** | `logs_page.py` | Browse and filter logs, export reports |
| **Settings** | `settings_page.py` | Configure detection rules, thresholds, appearance |
| **About** | `about_page.py` | Application info and credits |
| **Styles** | `styles.py` | Dark/light theme definitions |
| **Widgets** | `widgets.py` | Reusable custom widgets |

---

## 4. Data Flow

### 4.1 Connection Monitoring Flow
```
psutil.net_connections()
    → NetworkMonitor.get_connections()
        → Map PID to process name
            → Emit to Dashboard (via Qt Signal)
                → Update UI table
```

### 4.2 Intrusion Detection Flow
```
Connection data
    → RuleEngine.analyze()
        → Check against rules:
            • Beaconing detection (many IPs in short time)
            • Bad port detection (configurable list)
            • Connection rate limiting
        → If match: Create Alert
            → Store in SQLite
            → Emit to AlertsPage
            → Log to file
```

### 4.3 Firewall Rule Flow
```
User clicks "Block IP"
    → FirewallManager.block_ip(ip, direction)
        → Generate PowerShell command
        → Execute with subprocess
        → Parse result
    → Update Rules table
    → Log action
```

---

## 5. Detection Rules

### 5.1 Built-in Rules

| Rule ID | Name | Description | Threshold |
|---------|------|-------------|-----------|
| R001 | Beaconing Detection | Many unique IPs contacted in short time | >20 IPs in 60 sec |
| R002 | Bad Port Access | Connection to suspicious ports | Configurable list |
| R003 | High Connection Rate | Excessive new connections | >50 conn/min |
| R004 | Repeated Failed Logins | From Windows Event Log | >5 in 10 min |
| R005 | Known Bad IP | IP in threat intelligence list | User-managed list |

### 5.2 Alert Severity Levels

| Level | Color | Description |
|-------|-------|-------------|
| **LOW** | 🟢 Green | Informational, no action needed |
| **MEDIUM** | 🟡 Yellow | Suspicious, review recommended |
| **HIGH** | 🔴 Red | Likely threat, action recommended |
| **CRITICAL** | ⚫ Black/Red | Active attack, immediate action |

---

## 6. Windows Firewall Integration

### 6.1 PowerShell Commands Used

```powershell
# Block an IP (Inbound + Outbound)
New-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100" `
    -Direction Inbound -Action Block -RemoteAddress "192.168.1.100"

New-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100_Out" `
    -Direction Outbound -Action Block -RemoteAddress "192.168.1.100"

# Block a Port
New-NetFirewallRule -DisplayName "SaadFirewall_Block_Port_4444" `
    -Direction Inbound -Action Block -LocalPort 4444 -Protocol TCP

# List our rules
Get-NetFirewallRule -DisplayName "SaadFirewall_*"

# Remove a rule
Remove-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100"

# Enable/Disable a rule
Disable-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100"
Enable-NetFirewallRule -DisplayName "SaadFirewall_Block_IP_192.168.1.100"
```

### 6.2 Rule Naming Convention
All rules created by this app use the prefix: `SaadFirewall_`

Format: `SaadFirewall_<Action>_<Type>_<Value>[_Direction]`

Examples:
- `SaadFirewall_Block_IP_192.168.1.100`
- `SaadFirewall_Block_IP_192.168.1.100_Out`
- `SaadFirewall_Block_Port_4444_TCP`

---

## 7. Security Considerations

### 7.1 Privilege Requirements
- **Firewall operations**: Require Administrator
- **Event Log reading**: Require Administrator
- **Network monitoring**: Can run without admin (limited info)

### 7.2 Self-Protection
- Application validates all IP/port inputs
- PowerShell commands are parameterized (no injection)
- Logs are append-only
- Config changes require confirmation

---

## 8. Performance Considerations

- Network polling: Every 2 seconds (configurable)
- UI updates: Batched to prevent freezing
- Database: WAL mode for concurrent access
- Memory: Connection history limited to last 1000 entries

---

## 9. Folder Structure

```
Fire-wall/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── config.json               # Default configuration
├── README.md                 # User documentation
├── ARCHITECTURE.md           # This file
│
├── core/                     # Core business logic
│   ├── __init__.py
│   ├── network_monitor.py    # psutil-based connection monitor
│   ├── rule_engine.py        # Intrusion detection rules
│   ├── firewall_manager.py   # Windows Firewall integration
│   └── event_monitor.py      # Windows Event Log reader
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
│   ├── database.py           # SQLite database operations
│   └── helpers.py            # Helper functions
│
├── resources/                # Static resources
│   ├── icons/                # Application icons
│   └── styles/               # QSS stylesheets
│
├── logs/                     # Log files (created at runtime)
│   ├── app.log               # Human-readable log
│   └── events.jsonl          # JSON Lines event log
│
└── data/                     # Data files (created at runtime)
    └── alerts.db             # SQLite database
```

---

## 10. Arabic Summary (ملخص بالعربية)

### نظرة عامة على المشروع
هذا التطبيق هو **أداة أمنية دفاعية** مصممة لحماية أنظمة ويندوز من محاولات اختراق الشبكة.

### المكونات الرئيسية:
1. **مراقب الشبكة**: يراقب جميع الاتصالات النشطة في الوقت الفعلي
2. **محرك القواعد**: يكتشف الأنشطة المشبوهة تلقائياً
3. **مدير جدار الحماية**: يتحكم في جدار حماية ويندوز
4. **نظام التنبيهات**: ينبه المستخدم عند اكتشاف تهديد
5. **نظام السجلات**: يحفظ جميع الأحداث للمراجعة

### كيف يعمل:
- يقرأ الاتصالات النشطة كل ثانيتين
- يحلل الأنماط المشبوهة (مثل الاتصال بالكثير من العناوين)
- يُنشئ تنبيهات مع توصيات
- يمكن للمستخدم حظر عناوين IP مباشرة من التطبيق

---

*Document Version: 1.0*
*Last Updated: 2024*
