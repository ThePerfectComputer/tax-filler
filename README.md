# Tax Filler

This directory is the start of a standalone Form 1120 PDF-filling project.

## Current Status

The project can already:

- download and inspect the official IRS Form 1120 fillable PDF
- extract PDF field names and generate a draft field map
- fill the PDF from JSON using either raw field names or mapped labels
- fill checkbox fields using each widget's real PDF export state instead of assuming `/Yes`
- generate probe PDFs for low-confidence fields so a human can visually confirm them

The project does not yet have:

- a polished business-facing JSON schema
- a fully resolved field map for every field on the form
- a dedicated repository layout, tests, or packaging

## Files Kept

- `f1120.pdf`: source fillable IRS Form 1120 PDF
- `map_1120_fields.py`: field extraction and mapping logic
- `f1120-field-map.json`: current machine-readable field map
- `f1120-field-map-review.md`: current unresolved / low-confidence items
- `fill_pdf_from_json.py`: fill PDF from JSON values
  - now uses PyMuPDF widget updates so checkbox values render visibly in output PDFs
- `generate_low_confidence_probe.py`: generate review probes for unresolved fields
- `example-1120-values.json`: sample JSON input

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
python3 taxes/tax-filler/map_1120_fields.py
```

Fill the PDF from JSON:

```bash
python3 taxes/tax-filler/fill_pdf_from_json.py \
  --pdf taxes/tax-filler/f1120.pdf \
  --values taxes/tax-filler/example-1120-values.json \
  --field-map taxes/tax-filler/f1120-field-map.json \
  --output taxes/tax-filler/output.pdf
```

Generate a low-confidence probe package:

```bash
python3 taxes/tax-filler/generate_low_confidence_probe.py
```

## Low-Confidence Mappings

These are the remaining low-confidence or unresolved fields as of the current map:

1. Page 2
   - `topmostSubform[0].Page2[0].Table_ScheduleC[0].Line2[0].f2_5[0]`
     - current label: `Dividends from 20%-or-more-owned domestic corporations (other than debt-financed`
   - `topmostSubform[0].Page2[0].Table_ScheduleC[0].Line15[0].f2_44[0]`
     - current label: `Reserved for future use`
   - `topmostSubform[0].Page2[0].Table_ScheduleC[0].Line20[0].f2_65[0]`
     - current label: empty
   - `topmostSubform[0].Page2[0].Table_ScheduleC[0].Line22[0].f2_71[0]`
     - current label: `Section 250 deduction (attach Form 8993) (see instructions for limitations) Total dividends and inclusions Add column (a), lines 9 through 20 Enter here and on`

2. Page 4
   - `topmostSubform[0].Page4[0].c4_8[0]`
     - current label: `Schedule K line 7 Yes`
   - `topmostSubform[0].Page4[0].c4_8[1]`
     - current label: `Schedule K line 7 No`

3. Page 5
   - `topmostSubform[0].Page5[0].c5_4[1]`
     - current label: `b If "Yes," did or will the corporation file required Form(s) 1099?`
   - `topmostSubform[0].Page5[0].c5_17[0]`
     - current label: `Is the corporation a member of a controlled group? If "Yes," attach Schedule O (Form 1120) See instructions Corporate Alternative Minimum Tax:`
   - `topmostSubform[0].Page5[0].c5_17[1]`
     - current label: `Is the corporation a member of a controlled group? If "Yes," attach Schedule O (Form 1120) See instructions Corporate Alternative Minimum Tax:`
   - `topmostSubform[0].Page5[0].c5_25[0]`
     - current label: `in the instructions, of $10 million or more? If "Yes," attach a statement See instructions Reserved for future use`
   - `topmostSubform[0].Page5[0].c5_25[1]`
     - current label: `in the instructions, of $10 million or more? If "Yes," attach a statement See instructions Reserved for future use`

## Notes

- A substantial number of page 1, page 3, page 4 table, and page 6 Schedule L fields were confirmed manually using probe markers and screenshots.
- The most unresolved pieces now are page 2 text fields and page 4/page 5 checkboxes.
