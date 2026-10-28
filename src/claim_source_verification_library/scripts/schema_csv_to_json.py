#!/usr/bin/env python3
"""Turn the schema CSV (columns: "Field / label", "Definition") into the nested
schema template JSON, with each field's definition as its value.

Usage:
    uv run python schema_csv_to_json.py annotations.csv annotation.json
"""
import argparse
import json
import sys

import pandas as pd


def normalise(name):
    """'article_title:' / ' source_citation' / 'Rationale\\n' -> clean lowercase key."""
    return name.strip().rstrip(":").strip().lower()


def main():
    parser = argparse.ArgumentParser(description="Schema CSV -> nested schema JSON")
    parser.add_argument("input", help="path to the schema CSV")
    parser.add_argument("output", help="path for the JSON file")
    args = parser.parse_args()

    df = pd.read_csv(args.input, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    field_col, def_col = df.columns[0], df.columns[1]

    # field name -> definition
    d = {
        normalise(row[field_col]): row[def_col].strip()
        for _, row in df.iterrows()
        if row[field_col].strip()
    }

    def get(name):
        if name not in d:
            print(f"Warning: field '{name}' not found in the CSV", file=sys.stderr)
        return d.get(name)

    schema = {
        "claim_id": get("claim_id"),
        "article_title": get("article_title"),
        "claim_text": get("claim_text"),
        "origin": get("origin"),
        "origin_basis": get("origin_basis"),
        "annotations": [
            {
                "annotation_id": get("annotation_id"),
                "source_title": get("source_title"),
                "source_url": get("source_url"),
                "source_citation": get("source_citation"),
                "source_type": get("source_type"),
                "source_access": get("source_access"),
                "date_accessed": get("date_accessed"),
                "evidence": [
                    {
                        "excerpt": get("evidence_excerpt"),
                        "location": get("evidence_location"),
                    }
                ],
                "verdict": get("verdict"),
                "failure_type": [get("failure_type")],
                "rationale": get("rationale"),
            }
        ],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote schema to {args.output}")


if __name__ == "__main__":
    main()