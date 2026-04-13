# Tax Filler

This directory is the start of a standalone Form 1120 PDF-filling project.

## Current Status

The project can already:

- download and inspect the official IRS Form 1120 fillable PDF
- fill checkbox fields using each widget's real PDF export state instead of assuming `/Yes`
- accept nested, human-readable Form 1120 JSON schemas for 2024 and 2025

The project does not yet have:

- full friendly-schema coverage for every field on the form
- tests or packaging

## Layout

- `forms/f1120_2025.pdf`: 2025 fillable IRS Form 1120 PDF
- `forms/f1120_2024.pdf`: 2024 fillable IRS Form 1120 PDF
- `srcs/map_1120_fields.py`: field extraction and mapping logic
- `srcs/fill_pdf_from_json.py`: fill PDF from JSON values
  - uses PyMuPDF widget updates so checkbox values render visibly in output PDFs
- `srcs/friendly_1120_shared.py`: shared helpers for friendly Form 1120 schemas
- `srcs/friendly_1120_2024.py`: explicit 2024-friendly schema mapper
- `srcs/friendly_1120_2025.py`: explicit 2025-friendly schema mapper
- `examples/example-1120-friendly-2025.json`: nested friendly sample input for the 2025 form
- `examples/example-1120-friendly-2024.json`: nested friendly sample input for the 2024 form
- `srcs/map_1120_fields.py`: exploratory field-mapping script for deeper reverse-engineering work
- `srcs/generate_low_confidence_probe.py`: exploratory probe generator for unresolved fields

## Removed Clutter

These were deleted because they were generated artifacts and can be regenerated:

- filled demo PDFs
- filled JSON-output PDFs
- low-confidence probe output files
- debug page renders
- one-off demo filler script
- CSV export of the field map

## How To Regenerate

Rebuild the field map:

```bash
cd taxes/tax-filler
python3 srcs/map_1120_fields.py
```

Fill the PDF from JSON:

```bash
cd taxes/tax-filler
python3 srcs/fill_pdf_from_json.py \
  --pdf forms/f1120_2025.pdf \
  --values examples/example-1120-friendly-2025.json \
  --output output-friendly.pdf
```

Fill the 2024 PDF from friendly nested JSON:

```bash
cd taxes/tax-filler
python3 srcs/fill_pdf_from_json.py \
  --pdf forms/f1120_2024.pdf \
  --values examples/example-1120-friendly-2024.json \
  --output output-friendly-2024.pdf
```

The friendly schema currently supports:

- tax period begin/end dates
- company identity and address fields
- filing-status checkboxes on page 1
- core page 1 income and deduction lines
- page 1 payment / refund fields
- a substantial slice of Schedule J
- derived totals for core page 1 rollups and taxable income
- a broader set of Schedule K yes/no questions plus a few related amount fields
- separate explicit schema mappers for 2024 and 2025

Exploratory reverse-engineering tools still exist if deeper coverage work is needed:

```bash
cd taxes/tax-filler
python3 srcs/map_1120_fields.py
python3 srcs/generate_low_confidence_probe.py
```

## Notes

- The repo is now centered on year-specific friendly fillers rather than raw field-name inputs.
- 2025 support is currently broader than 2024.
- 2024 still has major uncovered sections, especially Schedule C on page 2 and large parts of page 6.
