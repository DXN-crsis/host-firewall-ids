<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=26&duration=3200&pause=900&color=58A6FF&center=true&vCenter=true&width=680&height=60&lines=SaadFirewall;Host+Firewall+%2B+Intrusion+Detection" alt="typing" />

Real-time host firewall and intrusion-detection system for Windows, with a
rule engine, live connection monitoring, and a PyQt dashboard.

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white" />
<img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" />

<img src="https://img.shields.io/github/languages/top/romeo2badboy-rgb/host-firewall-ids?style=flat-square&color=3776AB" />
<img src="https://img.shields.io/github/repo-size/romeo2badboy-rgb/host-firewall-ids?style=flat-square" />
<img src="https://img.shields.io/github/last-commit/romeo2badboy-rgb/host-firewall-ids?style=flat-square" />

</div>

## Overview

A defensive security tool that watches network connections in real time,
matches them against configurable rules, integrates with Windows Firewall, and
raises alerts. The interface is organized into dashboard, rules, alerts, logs,
and settings pages.

## Features

- Real-time network connection and event monitoring
- Rule-based intrusion detection with a dedicated rule engine
- Windows Firewall integration
- Centralized logging and alerting
- PyQt6 desktop interface

## Getting started

```bash
pip install -r requirements.txt
python main.py
```

## Structure

```
core/   monitoring, firewall, and rule-engine logic
ui/     PyQt6 pages, widgets, and styles
utils/  configuration helpers
```

See `ARCHITECTURE.md` for design details.
