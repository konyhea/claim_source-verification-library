#!/usr/bin/env python3
"""
Flat annotation sheet (CSV/TSV) -> nested claim/annotations/evidence JSON, using pandas.

Usage:
    uv run python annotations_to_json_pandas.py annotations_data.csv annotations.json
"""
import json
import re
import sys

import pandas as pd

VERDICTS = ["Supported", "Partially supported", "Not supported", "Unable to evaluate"]
SOURCE_TYPES = ["Journal article", "Thesis", "News article", "Book",
                "Government report", "Fact sheet", "Database", "Other"]
SOURCE_ACCESS = ["Full text", "Partial", "Paywalled", "Not found", "Other"]
FAILURE_TYPES = ["Missing evidence", "Unsupported number/statistic", "Unsupported causal link",
                 "Overstatement", "Unsupported scope or population", "Unsupported chronology",
                 "Contradiction"]
FAILURE_ALIASES = {"overstatement/stronger wording": "Overstatement",
                   "unsupported number/statistics": "Unsupported number/statistic"}
NO_PASSAGE = "NO SUPPORTING PASSAGE FOUND"

CLAIM_COLS = ["claim_id", "article_title", "claim_text", "origin", "origin_basis"]
ANN_COLS = ["annotation_id", "source_title", "source_url", "source_citation",
            "source_type", "source_access", "date_accessed"]

warnings = []


def clean(v):
    v = re.sub(r"\s+", " ", str(v)).strip()
    if len(v) > 1 and v[0] == '"' and v[-1] == '"':
        v = v[1:-1].strip()
    return v


def key(s):
    return re.sub(r"\s*/\s*", "/", s.strip().lower())


def canon(value, options, label, where, aliases=None):
    if not value:
        return ""
    k = key(value)
    if aliases and k in aliases:
        return aliases[k]
    for o in options:
        if key(o) == k:
            return o
    warnings.append(f"{where}: unrecognised {label} '{value}'")
    return value


def main(src, dst):
    with open(src, encoding="utf-8-sig") as f:
        first = f.readline()
    sep = "\t" if first.count("\t") > first.count(",") else ","

    df = pd.read_csv(src, sep=sep, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.columns = [re.sub(r"\s+", "_", c.strip().lower()) for c in df.columns]
    df = df.apply(lambda col: col.map(clean))          # clean every cell
    df = df[df.ne("").any(axis=1)]                     # drop fully blank rows

    # evidence pairs: excerpt_n / evidence_excerpts_n  +  location_n
    pairs = {}
    for c in df.columns:
        m = re.fullmatch(r"(?:evidence_)?excerpts?(?:_(\d+))?", c)
        if m:
            pairs.setdefault(int(m.group(1) or 1), {})["excerpt"] = c
        m = re.fullmatch(r"location(?:_(\d+))?", c)
        if m:
            pairs.setdefault(int(m.group(1) or 1), {})["location"] = c
    pairs = dict(sorted(pairs.items()))

    claims = []
    for claim_id, group in df.groupby("claim_id", sort=False):
        first_row = group.iloc[0]
        claim = {c: first_row.get(c, "") for c in CLAIM_COLS}
        claim["annotations"] = []

        for _, row in group.iterrows():
            where = f"claim {claim_id}, annotation {row.get('annotation_id', '')}"

            evidence = []
            for n, cols in pairs.items():
                excerpt = row.get(cols.get("excerpt", ""), "")
                location = row.get(cols.get("location", ""), "")
                if not excerpt and not location:
                    continue                            # skip empty pairs
                if not excerpt:
                    warnings.append(f"{where}: location_{n} has no excerpt")
                    continue
                if not location and excerpt != NO_PASSAGE:
                    warnings.append(f"{where}: excerpt_{n} has no location (null)")
                evidence.append({"excerpt": excerpt, "location": location or None})

            verdict = canon(row.get("verdict", ""), VERDICTS, "verdict", where)
            failure = [canon(p.strip().rstrip("."), FAILURE_TYPES, "failure_type", where,
                             FAILURE_ALIASES)
                       for p in re.split(r"[;]", row.get("failure_type", "")) if p.strip()]

            if not evidence:
                if verdict == "Not supported":
                    evidence = [{"excerpt": NO_PASSAGE, "location": None}]
                else:
                    warnings.append(f"{where}: no evidence recorded")
            if verdict in ("Supported", "Unable to evaluate") and failure:
                warnings.append(f"{where}: failure_type should be empty for '{verdict}'")
            if verdict in ("Partially supported", "Not supported") and not failure:
                warnings.append(f"{where}: failure_type empty for '{verdict}'")
            if not row.get("rationale", ""):
                warnings.append(f"{where}: empty rationale")

            ann = {c: row.get(c, "") for c in ANN_COLS}
            ann["source_type"] = canon(ann["source_type"], SOURCE_TYPES, "source_type", where)
            ann["source_access"] = canon(ann["source_access"], SOURCE_ACCESS,
                                         "source_access", where)
            ann.update(evidence=evidence, verdict=verdict, failure_type=failure,
                       rationale=row.get("rationale", ""))
            claim["annotations"].append(ann)

        claims.append(claim)

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(claims, f, indent=2, ensure_ascii=False)
        f.write("\n")

    n_ann = sum(len(c["annotations"]) for c in claims)
    print(f"Wrote {len(claims)} claims / {n_ann} annotations to {dst}")
    for w in warnings:
        print(f"  warning: {w}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])