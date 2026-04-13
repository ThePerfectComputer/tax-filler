# Tax Filler

This directory is the start of a standalone Form 1120 PDF-filling project.

## Current Status

The project can already:

- download and inspect the official IRS Form 1120 fillable PDF
- fill checkbox fields using each widget's real PDF export state instead of assuming `/Yes`
- accept nested, human-readable Form 1120 JSON schemas for 2024 and 2025
- cover every fillable widget in both the 2024 and 2025 source PDFs

The project does not yet have:

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
- page 1 income, deduction, tax, payment, refund, and signing areas
- Schedule C
- Schedule J
- Schedule K
- Schedule L
- Schedule M-1
- Schedule M-2
- derived totals for core page 1 rollups and taxable income
- separate explicit schema mappers for 2024 and 2025
- choice-style checkbox groups such as accounting method and refund account type

Exploratory reverse-engineering tools still exist if deeper coverage work is needed:

```bash
cd taxes/tax-filler
python3 srcs/map_1120_fields.py
python3 srcs/generate_low_confidence_probe.py
```

## Notes

- The repo is now centered on year-specific friendly fillers rather than raw field-name inputs.
- Both 2024 and 2025 now have full widget coverage.
- Full widget coverage means every fillable PDF field is reachable through the friendly schema layer or a derived field path.
- A few 2024 labels remain intentionally conservative or generic where the IRS widget structure is awkward, especially in parts of Schedule K and the paid preparer block.
