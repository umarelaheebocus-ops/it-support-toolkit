"""System health report: disk space, service status and network ports.

Usage:
    python -m itkit.health_check --disk / --port localhost:22 --service ssh
"""
import argparse
import json
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime


def check_disk(path, warn_pct=80):
    total, used, free = shutil.disk_usage(path)
    pct = used / total * 100
    return {"check": "disk", "target": path, "used_pct": round(pct, 1),
            "free_gb": round(free / 1e9, 1),
            "status": "WARN" if pct >= warn_pct else "OK"}


def check_port(host, port, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            status = "OK"
    except OSError:
        status = "DOWN"
    return {"check": "port", "target": f"{host}:{port}", "status": status}


def check_service(name):
    """Uses systemctl on Linux; reports UNKNOWN elsewhere."""
    if shutil.which("systemctl") is None:
        return {"check": "service", "target": name, "status": "UNKNOWN"}
    result = subprocess.run(["systemctl", "is-active", name],
                            capture_output=True, text=True)
    state = result.stdout.strip()
    return {"check": "service", "target": name,
            "status": "OK" if state == "active" else state.upper() or "UNKNOWN"}


def build_report(disks, ports, services, warn_pct=80):
    results = [check_disk(d, warn_pct) for d in disks]
    for p in ports:
        host, _, port = p.rpartition(":")
        results.append(check_port(host or "localhost", int(port)))
    results += [check_service(s) for s in services]
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--disk", action="append")
    ap.add_argument("--port", action="append", default=[], help="host:port")
    ap.add_argument("--service", action="append", default=[])
    ap.add_argument("--warn", type=int, default=80, help="disk warning %%")
    ap.add_argument("--json", action="store_true", help="output JSON")
    args = ap.parse_args(argv)

    results = build_report(args.disk or ["/"], args.port, args.service, args.warn)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Health report - {platform.node()} - {datetime.now():%Y-%m-%d %H:%M}")
        print("-" * 56)
        for r in results:
            extra = (f"{r['used_pct']}% used, {r['free_gb']} GB free"
                     if r["check"] == "disk" else "")
            print(f"[{r['status']:<7}] {r['check']:<8} {r['target']:<20} {extra}")
    return 0 if all(r["status"] in ("OK", "UNKNOWN") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
