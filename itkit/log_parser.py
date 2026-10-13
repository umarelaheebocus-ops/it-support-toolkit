"""Parse an application log and summarise errors and suspicious logins.

Expected line format:
    2026-10-13 09:15:02 ERROR [auth] Failed login for user admin from 10.0.0.5

Usage:
    python -m itkit.log_parser data/sample.log --threshold 3
"""
import argparse
import re
import sys
from collections import Counter

LINE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>[\d:]{8}) "
    r"(?P<level>[A-Z]+) \[(?P<component>[\w-]+)\] (?P<msg>.*)$")
FAILED_LOGIN_RE = re.compile(r"Failed login for user (\S+) from (\d+\.\d+\.\d+\.\d+)")


def parse_lines(lines, threshold=3):
    levels, errors, failed_ips, bad = Counter(), Counter(), Counter(), 0
    for line in lines:
        m = LINE_RE.match(line.strip())
        if not m:
            bad += 1
            continue
        levels[m["level"]] += 1
        if m["level"] in ("ERROR", "CRITICAL"):
            errors[f"[{m['component']}] {m['msg']}"] += 1
        f = FAILED_LOGIN_RE.search(m["msg"])
        if f:
            failed_ips[f.group(2)] += 1
    suspicious = {ip: n for ip, n in failed_ips.items() if n >= threshold}
    return {"levels": dict(levels), "top_errors": errors.most_common(5),
            "suspicious_ips": suspicious, "unparsed": bad}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("log_file")
    ap.add_argument("--threshold", type=int, default=3,
                    help="failed logins from one IP before it is flagged")
    args = ap.parse_args(argv)
    with open(args.log_file, encoding="utf-8") as f:
        r = parse_lines(f, args.threshold)

    print("Log summary")
    print("-" * 40)
    for level, n in sorted(r["levels"].items()):
        print(f"{level:<9}{n}")
    print("\nTop errors:")
    for msg, n in r["top_errors"]:
        print(f"  {n}x {msg}")
    print("\nSuspicious IPs (repeated failed logins):")
    for ip, n in r["suspicious_ips"].items():
        print(f"  {ip}: {n} failures")
    if r["unparsed"]:
        print(f"\n{r['unparsed']} line(s) could not be parsed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
