#!/usr/bin/env python3
"""Convert the claim-source annotation CSV into JSON using pandas.

Usage:
    python csv_to_json.py annotations.csv annotations.json
"""
import argparse
import json
import sys

import pandas as pd

LIST_FIELDS = ["failure_type"]

ALLOWED = {
    "verdict": {"Supported", "Partially supported", "Not supported", "Unable to evaluate"},
    "source_access": {"Full text", "Partial", "Paywalled", "Not found", "Other"},
    "origin": {"AI-flagged", "Organic sample"},
}


def main():
    parser = argparse.ArgumentParser(description="Convert annotation CSV to JSON")
    parser.add_argument("input", help="path to the CSV file")
    parser.add_argument("output", help="path for the JSON file")
    args = parser.parse_args()

    # dtype=str keeps IDs like "001" intact; utf-8-sig strips Excel's BOM
    df = pd.read_csv(args.input, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = df.apply(lambda col: col.str.strip())

    # Warn on unexpected controlled values
    for col, allowed in ALLOWED.items():
        if col in df.columns:
            bad = df[(df[col] != "") & (~df[col].isin(allowed))]
            for idx, val in bad[col].items():
                print(f"Warning (row {idx + 2}): unexpected {col} value '{val}'", file=sys.stderr)

    # Split multi-label cells into lists
    for col in LIST_FIELDS:
        if col in df.columns:
            df[col] = df[col].apply(lambda s: [v.strip() for v in s.split(";") if v.strip()])

    # Empty strings -> None (lists are left as they are)
    records = [
        {k: (None if v == "" else v) for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(records)} annotations to {args.output}")


if __name__ == "__main__":
    main()