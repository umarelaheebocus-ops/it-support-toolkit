"""Bulk user provisioning from a CSV file.

Reads new-starter details, validates them, generates unique usernames and
temporary passwords, and writes a provisioning report. By default it only
plans the work (dry run); --commands prints the Linux `useradd` commands an
admin would run.

Usage:
    python -m itkit.create_users data/users.csv --out provisioning_report.csv
"""
import argparse
import csv
import re
import secrets
import string
import sys

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
REQUIRED = {"first_name", "last_name", "department", "email"}


def make_username(first, last, taken):
    """first initial + surname, lowercase; add a number if already taken."""
    base = re.sub(r"[^a-z]", "", (first[:1] + last).lower())
    username, n = base, 1
    while username in taken:
        n += 1
        username = f"{base}{n}"
    return username


def make_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in pw) and any(c.isupper() for c in pw)
                and any(c.isdigit() for c in pw)):
            return pw


def process_users(rows):
    """Return (accounts, errors) from an iterable of CSV row dicts."""
    accounts, errors, taken = [], [], set()
    for line_no, row in enumerate(rows, start=2):  # line 1 is the header
        first = (row.get("first_name") or "").strip()
        last = (row.get("last_name") or "").strip()
        dept = (row.get("department") or "").strip()
        email = (row.get("email") or "").strip()
        if not (first and last and dept):
            errors.append((line_no, "missing name or department"))
            continue
        if not EMAIL_RE.match(email):
            errors.append((line_no, f"invalid email '{email}'"))
            continue
        username = make_username(first, last, taken)
        taken.add(username)
        accounts.append({
            "username": username, "full_name": f"{first} {last}",
            "department": dept, "email": email,
            "temp_password": make_password(),
        })
    return accounts, errors


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("csv_file")
    p.add_argument("--out", default="provisioning_report.csv")
    p.add_argument("--commands", action="store_true",
                   help="print Linux useradd commands (nothing is executed)")
    args = p.parse_args(argv)

    with open(args.csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not REQUIRED.issubset(reader.fieldnames or []):
            sys.exit(f"CSV must contain columns: {', '.join(sorted(REQUIRED))}")
        accounts, errors = process_users(reader)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["username", "full_name", "department",
                                          "email", "temp_password"])
        w.writeheader()
        w.writerows(accounts)

    print(f"Planned {len(accounts)} accounts -> {args.out}")
    for line_no, reason in errors:
        print(f"  SKIPPED line {line_no}: {reason}")
    if args.commands:
        for a in accounts:
            print(f"sudo useradd -m -c '{a['full_name']}' -G {a['department'].lower()} {a['username']}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
