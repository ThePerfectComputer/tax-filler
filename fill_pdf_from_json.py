from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def build_lookup(field_map_rows: list[dict]) -> tuple[dict[str, str], dict[str, dict]]:
    lookup: dict[str, str] = {}
    metadata: dict[str, dict] = {}
    for row in field_map_rows:
        field_name = row["field_name"]
        metadata[field_name] = row
        label = row.get("label", "")
        lookup[field_name] = field_name
        if label:
            lookup[label] = field_name
            lookup[slugify(label)] = field_name
    return lookup, metadata


def normalize_value(value, field_type: str | None):
    if field_type == "CheckBox":
        return value
    return "" if value is None else str(value)


def resolve_values(values: dict, field_map_rows: list[dict] | None) -> dict[str, object]:
    if not field_map_rows:
        return values.copy()

    lookup, metadata = build_lookup(field_map_rows)
    resolved: dict[str, object] = {}
    unknown: list[str] = []
    for key, value in values.items():
        field_name = lookup.get(key) or lookup.get(slugify(key))
        if field_name is None:
            unknown.append(key)
            continue
        field_type = metadata.get(field_name, {}).get("field_type")
        resolved[field_name] = normalize_value(value, field_type)

    if unknown:
        unknown_text = ", ".join(sorted(unknown))
        raise SystemExit(f"Unrecognized JSON keys: {unknown_text}")
    return resolved


def checkbox_state_for_value(widget: fitz.Widget, value) -> str:
    if value in (False, "false", "False", "no", "No", "off", "Off", 0, "0", "/Off", None, ""):
        return "Off"

    if isinstance(value, str):
        candidate = value.lstrip("/")
        states = widget.button_states().get("normal", [])
        if candidate in states:
            return candidate

    return str(widget.on_state())


def fill_pdf(input_pdf: Path, output_pdf: Path, resolved_values: dict[str, object]) -> None:
    pdf = fitz.open(str(input_pdf))

    for page in pdf:
        for widget in page.widgets():
            value = resolved_values.get(widget.field_name)
            if value is None and widget.field_name not in resolved_values:
                continue

            if widget.field_type_string == "CheckBox":
                state = checkbox_state_for_value(widget, value)
                widget.field_value = state
            else:
                widget.field_value = "" if value is None else str(value)
            widget.update()

    pdf.save(str(output_pdf), garbage=4, deflate=True)
    pdf.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fill a fillable PDF from a JSON object.")
    parser.add_argument("--pdf", required=True, help="Path to the input PDF.")
    parser.add_argument("--values", required=True, help="Path to the JSON file containing field values.")
    parser.add_argument("--output", required=True, help="Path to the output filled PDF.")
    parser.add_argument(
        "--field-map",
        help="Optional field-map JSON. If supplied, JSON keys may be raw field names, exact labels, or slugified labels.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_pdf = Path(args.pdf).resolve()
    values_path = Path(args.values).resolve()
    output_pdf = Path(args.output).resolve()
    field_map_path = Path(args.field_map).resolve() if args.field_map else None

    values = json.loads(values_path.read_text(encoding="utf-8"))
    if not isinstance(values, dict):
        raise SystemExit("Values JSON must be an object mapping keys to values.")

    field_map_rows = None
    if field_map_path:
        field_map_rows = json.loads(field_map_path.read_text(encoding="utf-8"))
        if not isinstance(field_map_rows, list):
            raise SystemExit("Field map JSON must be a list of field metadata rows.")

    resolved_values = resolve_values(values, field_map_rows)
    fill_pdf(input_pdf, output_pdf, resolved_values)

    print(f"Wrote {output_pdf}")
    print(f"Filled {len(resolved_values)} fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
