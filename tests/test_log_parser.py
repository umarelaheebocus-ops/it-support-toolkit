from itkit.log_parser import parse_lines

LOG = [
    "2026-10-13 09:00:00 ERROR [auth] Failed login for user a from 1.2.3.4",
    "2026-10-13 09:00:01 ERROR [auth] Failed login for user b from 1.2.3.4",
    "2026-10-13 09:00:02 ERROR [auth] Failed login for user c from 1.2.3.4",
    "2026-10-13 09:00:03 INFO [web] ok",
    "garbage",
]


def test_counts_levels_and_unparsed_lines():
    r = parse_lines(LOG)
    assert r["levels"] == {"ERROR": 3, "INFO": 1} and r["unparsed"] == 1


def test_flags_ip_over_threshold():
    assert parse_lines(LOG, threshold=3)["suspicious_ips"] == {"1.2.3.4": 3}
    assert parse_lines(LOG, threshold=4)["suspicious_ips"] == {}
