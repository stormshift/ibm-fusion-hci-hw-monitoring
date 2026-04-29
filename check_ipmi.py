#!/usr/bin/env python3

import argparse
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Nagios-style check via ipmitool sdr entity (lanplus).",
    )
    parser.add_argument("-H", "--host", required=True, help="BMC / IPMI host")
    parser.add_argument("-U", "--user", required=True, help="IPMI user")
    parser.add_argument("-P", "--password", required=True, help="IPMI password")
    parser.add_argument(
        "-E",
        "--entity",
        required=True,
        help="Sensor entity id (e.g. 39.1) for: sdr entity <id> -c",
    )
    parser.add_argument(
        "-W",
        "--warning",
        type=float,
        required=True,
        help="Warning threshold (upper bound; value >= W and < C)",
    )
    parser.add_argument(
        "-C",
        "--critical",
        type=float,
        required=True,
        help="Critical threshold (upper bound; value >= C)",
    )
    args = parser.parse_args()
    w, c = args.warning, args.critical
    if w >= c:
        print(f"UNKNOWN - invalid thresholds: warning ({w}) must be less than critical ({c})")
        return 3

    cmd = [
        "ipmitool",
        "-H",
        args.host,
        "-U",
        args.user,
        "-P",
        args.password,
        "-I",
        "lanplus",
        "sdr",
        "entity",
        args.entity,
        "-c",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as e:
        print(f"UNKNOWN - failed to run ipmitool: {e}")
        return 3

    if result.returncode != 0:
        err = (result.stderr or "").strip() or f"exit {result.returncode}"
        out = (result.stdout or "").strip()[:200]
        detail = f"; stdout={out!r}" if out else ""
        print(f"UNKNOWN - ipmitool failed: {err}{detail}")
        return 3

    first_line = None
    for line in (result.stdout or "").splitlines():
        s = line.strip()
        if s:
            first_line = s
            break

    if not first_line:
        print("UNKNOWN - ipmitool returned no data")
        return 3

    parts = [p.strip() for p in first_line.split(",")]
    if len(parts) < 3:
        print(f"UNKNOWN - unparseable ipmitool line: {first_line!r}")
        return 3

    name, value_s, unit = parts[0], parts[1], parts[2]
    try:
        value = float(value_s)
    except ValueError:
        print(f"UNKNOWN - not a numeric value: {value_s!r}")
        return 3

    if value >= c:
        state = "CRITICAL"
        code = 2
    elif value >= w:
        state = "WARNING"
        code = 1
    else:
        state = "OK"
        code = 0

    label = name.replace(" ", "_")
    display_val = int(value) if value.is_integer() else value

    print(
        f"{state} - {name} {display_val} {unit} | {label}={value};{w};{c}"
    )
    return code


if __name__ == "__main__":
    sys.exit(main())
