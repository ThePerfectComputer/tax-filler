from __future__ import annotations

import json
import re
from pathlib import Path

from fill_pdf_from_json import fill_pdf


ROOT = Path(__file__).resolve().parent
FIELD_MAP_PATH = ROOT / "f1120-field-map.json"
INPUT_PDF = ROOT / "f1120.pdf"
OUTPUT_PDF = ROOT / "f1120-low-confidence-probe.pdf"
OUTPUT_JSON = ROOT / "f1120-low-confidence-probe-values.json"
OUTPUT_MANIFEST = ROOT / "f1120-low-confidence-probe-manifest.json"
OUTPUT_REVIEW = ROOT / "f1120-low-confidence-probe-review.md"


def is_flagged(row: dict) -> bool:
    label = row.get("label", "")
    return (
        not label
        or row.get("confidence", 0.0) < 0.7
        or "www.irs.gov" in label.lower()
        or re.fullmatch(r"[0-9]+[a-z]?", label.lower()) is not None
    )


def main() -> int:
    rows = json.loads(FIELD_MAP_PATH.read_text(encoding="utf-8"))
    flagged = [row for row in rows if is_flagged(row)]

    values: dict[str, object] = {}
    manifest: list[dict] = []
    text_counter = 1
    checkbox_counter = 1

    for row in flagged:
        field_name = row["field_name"]
        field_type = row["field_type"]
        page = row["page"]
        label = row.get("label", "")

        if field_type == "CheckBox":
            marker = f"CHK{checkbox_counter:02d}"
            value = True
            checkbox_counter += 1
        else:
            marker = f"LC{page:02d}_{text_counter:03d}"
            value = marker
            text_counter += 1

        values[field_name] = value
        manifest.append(
            {
                "marker": marker,
                "field_name": field_name,
                "field_type": field_type,
                "page": page,
                "label": label,
                "confidence": row.get("confidence", 0.0),
                "value": value,
            }
        )

    OUTPUT_JSON.write_text(json.dumps(values, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    resolved_values = {}
    for entry in manifest:
        if entry["field_type"] == "CheckBox":
            resolved_values[entry["field_name"]] = "/Yes"
        else:
            resolved_values[entry["field_name"]] = entry["value"]

    fill_pdf(INPUT_PDF, OUTPUT_PDF, resolved_values)

    lines = [
        "# Form 1120 Low-Confidence Probe",
        "",
        f"Flagged fields: {len(manifest)}",
        "",
        "Text markers to locate in the PDF:",
        "",
    ]
    for entry in manifest:
        if entry["field_type"] != "CheckBox":
            label = entry["label"] or "(no current label)"
            lines.append(
                f"- `{entry['marker']}` -> page {entry['page']} -> `{entry['field_name']}` -> `{label}`"
            )
    lines.extend(
        [
            "",
            "Checkbox probes:",
            "",
        ]
    )
    for entry in manifest:
        if entry["field_type"] == "CheckBox":
            label = entry["label"] or "(no current label)"
            lines.append(
                f"- `{entry['marker']}` checked -> page {entry['page']} -> `{entry['field_name']}` -> `{label}`"
            )
    OUTPUT_REVIEW.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_MANIFEST}")
    print(f"Wrote {OUTPUT_REVIEW}")
    print(f"Wrote {OUTPUT_PDF}")
    print(f"Text markers: {text_counter - 1}")
    print(f"Checkbox probes: {checkbox_counter - 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
