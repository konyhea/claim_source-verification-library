# Claim-Source Verification Library

This repository contains a dataset and annotation framework for evaluating how well sources cited in Wikipedia articles support their associated claims.

The project focuses on building a collection of human-reviewed claim–source pairs, with evidence excerpts, verdicts, and rationales documenting how each source supports or fails to support a claim.

The dataset is intended to support the development and evaluation of automated systems for identifying claims that are insufficiently supported by their cited sources, including claims appearing in AI-generated content.

## Repository Structure

The repository is organised into three main directories:

- **`data/`** – Contains the annotation data and dataset files in CSV and JSON formats.
- **`docs/`** – Contains the annotation guidelines and schema documentation, including instructions for evaluating claim–source pairs.
- **`scripts/`** – Contains Python scripts for converting CSV data into JSON format.

## Dataset Format

The dataset is formatted as JSON. Each record represents a Wikipedia claim and its associated source annotations.

A claim can have multiple cited sources. Each source is evaluated independently, with a unique `annotation_id` assigned to every claim–source pair. The same `claim_id` is retained across annotations belonging to the same claim.

Each claim follows the structure below:

```json
{
  "claim_id": "ID of the claim; reused if the same claim has several sources",
  "article_title": "Title of the Wikipedia article containing the claim",
  "claim_text": "Exact claim being checked; split compound sentences into separate claims",
  "origin": "AI-flagged / Organic sample",
  "annotations": [
    {
      "annotation_id": "Unique ID for this claim–source evaluation",
      "source_title": "Title as shown by the source",
      "source_url": "URL as cited",
      "source_type": "Journal article / Thesis / News article / Book / Government report / Fact sheet / Database / Other",
      "source_access": "Full text / Partial / Paywalled / Not found / Other",
      "date_accessed": "Date the source was checked",
      "evidence": [
        {
          "excerpt": "Short exact quote(s), or NO SUPPORTING PASSAGE FOUND",
          "location": "Page, section or paragraph of the excerpt"
        }
      ],
      "verdict": "Supported / Partially supported / Not supported / Unable to evaluate",
      "failure_type": [
        "Missing evidence / Unsupported number or statistic / Unsupported causal link / Overstatement / Unsupported scope or population / Contradiction"
      ],
      "rationale": "2–3 sentences explaining what the source establishes and what it does not"
    }
  ]
}
```

### Field Descriptions

| Field | Description |
|---|---|
| `claim_id` | Unique identifier for a claim. Reused when the same claim has multiple cited sources. |
| `article_title` | Title of the Wikipedia article containing the claim. |
| `claim_text` | Exact wording of the claim being evaluated. |
| `origin` | Indicates how the claim was selected: AI-flagged or Organic sample. This does not establish authorship. |
| `annotation_id` | Unique identifier for each claim–source evaluation. |
| `source_title` | Title of the cited source. |
| `source_url` | URL of the cited source. |
| `source_type` | Classification of the source. |
| `source_access` | Records the level of access available during evaluation. |
| `date_accessed` | Date the source was checked. |
| `evidence` | Contains relevant excerpts from the source and their locations. |
| `verdict` | Assessment of how well the source supports the claim. |
| `failure_type` | Describes how the source fails to establish the claim, where applicable. |
| `rationale` | Brief explanation of the verdict, identifying what the source establishes and what it does not. |

## Annotation Framework

Each claim–source pair is evaluated using four possible verdicts:

- **Supported:** The source provides evidence for all important parts of the claim.
- **Partially supported:** The source supports some parts of the claim but does not establish others, or supports a less specific version.
- **Not supported:** The source provides no evidence for the claim or explicitly contradicts it.
- **Unable to evaluate:** There is insufficient accessible information to determine whether the source supports the claim.

Failure types help explain why a source does not fully establish a claim. Multiple failure types may be assigned when applicable.

The annotation process prioritises evidence from the cited source. It does not independently fact-check claims against other sources or evaluate the credibility and overall quality of the cited source.

## Annotation Guidelines

The `docs/annotation-guidelines.md` file provides instructions for annotating claim–source pairs. It covers:

- The annotation process and evaluation steps.
- How to assign verdicts.
- How to identify and record supporting evidence.
- Failure types and their definitions.
- Edge cases and additional annotation rules.
- Examples of supported, partially supported, not supported, and unable-to-evaluate annotations.

The `docs/annotation_schema.json` file provides the initial JSON schema template and describes the expected structure of an annotation record.

## Scripts

The `scripts/` directory contains Python utilities for converting CSV data into JSON.

- `csv_to_json.py`
- `schema_csv_to_json.py`

These scripts support the preparation of structured JSON files from CSV inputs.