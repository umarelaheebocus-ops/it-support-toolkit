import socket
from itkit.health_check import check_disk, check_port


def test_disk_check_returns_valid_status():
    r = check_disk("/")
    assert r["status"] in ("OK", "WARN") and 0 <= r["used_pct"] <= 100


def test_disk_warns_when_threshold_is_zero():
    assert check_disk("/", warn_pct=0)["status"] == "WARN"


def test_port_check_detects_open_and_closed_ports():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    s.listen(1)
    open_port = s.getsockname()[1]
    assert check_port("127.0.0.1", open_port)["status"] == "OK"
    s.close()
    assert check_port("127.0.0.1", open_port, timeout=0.5)["status"] == "DOWN"
