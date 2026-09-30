#!/usr/bin/env python3
"""Compare the header rows of two CSV files.

Usage:
    python compare_headers.py expected_orders.csv actual_orders.csv
"""
import csv
import os
import sys


class HeaderError(Exception):
    """Raised for problems the user should be told about clearly."""


def parse_headers(line):
    """Split a raw first row into trimmed, non-empty headers."""
    row = next(csv.reader([line.strip("\r\n")]), [])
    return [cell.strip() for cell in row if cell.strip()]


def read_headers(path):
    """Read only the first row of a CSV file and return its headers."""
    if not os.path.exists(path):
        raise HeaderError(f"File not found: {path}")
    if not os.path.isfile(path):
        raise HeaderError(f"Not a file: {path}")
    try:
        # utf-8-sig strips a BOM; newline="" keeps \r\n handling predictable.
        with open(path, encoding="utf-8-sig", newline="") as f:
            first_line = f.readline()
    except (OSError, UnicodeDecodeError) as exc:
        raise HeaderError(f"Could not read {path}: {exc}")

    if first_line == "":
        raise HeaderError(f"File is empty: {path}")
    headers = parse_headers(first_line)
    if not headers:
        raise HeaderError(f"First row of {path} contains no valid headers")
    return headers


def compare_headers(expected, actual):
    """Compare two header lists. Order of results follows file order."""
    actual_set, expected_set = set(actual), set(expected)
    only_expected = [h for h in dict.fromkeys(expected) if h not in actual_set]
    only_actual = [h for h in dict.fromkeys(actual) if h not in expected_set]
    common = [h for h in dict.fromkeys(expected) if h in actual_set]
    common_in_actual = [h for h in dict.fromkeys(actual) if h in expected_set]
    return {
        "only_in_expected": only_expected,
        "only_in_actual": only_actual,
        "common": common,
        "same_order": common == common_in_actual,
    }


def format_report(result):
    def fmt(items):
        return ", ".join(items) if items else "(none)"

    return "\n".join([
        f"Only in expected: {fmt(result['only_in_expected'])}",
        f"Only in actual:   {fmt(result['only_in_actual'])}",
        f"In both:          {fmt(result['common'])}",
        "Common headers in same relative order: "
        + ("YES" if result["same_order"] else "NO"),
    ])


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("Error: expected exactly two file paths.", file=sys.stderr)
        print("Usage: python compare_headers.py <expected.csv> <actual.csv>",
              file=sys.stderr)
        return 2
    try:
        expected = read_headers(argv[0])
        actual = read_headers(argv[1])
    except HeaderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(format_report(compare_headers(expected, actual)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
