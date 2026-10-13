# IT Support Toolkit

![CI](https://github.com/umarelaheebocus-ops/it-support-toolkit/actions/workflows/ci.yml/badge.svg)

Small Python command-line tools that automate common helpdesk and sysadmin tasks.
Standard library only, with automated tests and CI.

| Tool | What it does |
|------|--------------|
| `create_users` | Reads new-starter details from a CSV, validates them, generates unique usernames and temporary passwords, and writes a provisioning report. Invalid rows are skipped and reported. |
| `health_check` | Reports disk usage (with warning threshold), TCP port reachability and service status. Exit code is non-zero if anything fails, so it can run in cron/monitoring. |
| `log_parser` | Summarises log levels, the most frequent errors, and flags IPs with repeated failed logins. |

## Setup
```bash
git clone https://github.com/umarelaheebocus-ops/it-support-toolkit.git
cd it-support-toolkit
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```bash
python -m itkit.create_users data/users.csv --commands
python -m itkit.health_check --disk / --port localhost:22 --service ssh
python -m itkit.log_parser data/sample.log --threshold 3
python -m pytest -v
```

## Design notes
- `create_users` is a dry run by design: it plans accounts and prints the `useradd`
  commands rather than executing them, so it is safe to demo without admin rights.
- Temporary passwords come from Python's `secrets` module. In real use they should be
  delivered via a secure channel and forced to change at first login.
- Service checks use `systemctl` (Linux) and report `UNKNOWN` on other systems.

## Ideas for extension
Email the health report, add a Windows `net user` / PowerShell output mode,
package it in a Docker container, or schedule it with cron.
