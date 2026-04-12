# AGENTS.md

This directory is the beginning of a standalone Form 1120 PDF-filling project.

The immediate goal is:

1. maintain a high-quality machine-readable field map for IRS Form 1120
2. support filling the form from JSON
3. eventually expose a cleaner business-facing schema that compiles into raw PDF fields

## Directory Intent

Treat this directory as an emerging repo boundary.

Keep it focused on:

- source PDF
- field extraction and mapping logic
- JSON-to-PDF filling logic
- review/probe generation logic
- project documentation

Avoid dumping regenerated output PDFs, screenshots, or other bulky scratch artifacts here long-term unless they are needed for debugging in the current session.

## Current Important Files

- `f1120.pdf`
  - Official IRS fillable PDF currently used as the source form.

- `map_1120_fields.py`
  - Main field-mapping script.
  - Uses a mix of PDF field introspection, geometry matching, page-specific overrides, OCR-assisted fallback, and manually confirmed overrides.

- `f1120-field-map.json`
  - Current machine-readable field map.

- `f1120-field-map-review.md`
  - Current low-confidence / unresolved items.

- `fill_pdf_from_json.py`
  - Fills the PDF from JSON values.
  - Accepts raw field names, exact labels, or slugified labels when a field map is supplied.

- `generate_low_confidence_probe.py`
  - Generates probe values for unresolved fields so they can be visually confirmed.

- `README.md`
  - Current project status and unresolved field summary.

- `STRATEGIES.md`
  - Extraction and validation strategies used so far and recommended going forward.

## What Has Already Been Learned

Several fields that were originally ambiguous have already been confirmed manually using:

- unique text probes
- rendered PDF screenshots
- human review of screenshots

Those confirmations were baked back into `map_1120_fields.py` as hard overrides.

Do not throw those away by replacing confirmed overrides with lower-confidence heuristic guesses.

## Current Remaining Low-Confidence Areas

As of the latest run, the unresolved/low-confidence items are concentrated in:

1. Page 2 text fields
   - several Schedule C entries

2. Page 4 checkboxes
   - Schedule K line 7 yes/no pair

3. Page 5 checkboxes
   - a few yes/no pairs whose question text still needs precise confirmation

Always check the latest `f1120-field-map-review.md` instead of relying on memory.

## Recommended Working Style

When continuing this project:

1. Regenerate the current map before making major conclusions:

```bash
python3 taxes/tax-filler/map_1120_fields.py
```

2. Read the review file:

```bash
sed -n '1,200p' taxes/tax-filler/f1120-field-map-review.md
```

3. If needed, generate a fresh probe package:

```bash
python3 taxes/tax-filler/generate_low_confidence_probe.py
```

4. Prefer composable strategies:
   - geometry matching
   - page-specific structural rules
   - localized probe/render/crop/inspect
   - OCR fallback
   - human confirmation only where ambiguity remains

5. After confirming fields, bake them back into hard overrides in `map_1120_fields.py`, rerun the mapper, and confirm they disappear from the review list.

## Filling Workflow

Current filler command:

```bash
python3 taxes/tax-filler/fill_pdf_from_json.py \
  --pdf taxes/tax-filler/f1120.pdf \
  --values taxes/tax-filler/example-1120-values.json \
  --field-map taxes/tax-filler/f1120-field-map.json \
  --output taxes/tax-filler/output.pdf
```

This currently works for direct label-based and slug-based JSON keys.

## Near-Term Next Steps

The most useful next steps are:

1. finish resolving the remaining low-confidence fields
2. improve checkbox verification on pages 4 and 5
3. define a canonical JSON schema that is more tax-domain-friendly than raw field labels
4. add lightweight project packaging such as:
   - `requirements.txt` or `pyproject.toml`
   - a small README usage example
   - maybe a simple test or validation script

## Things To Avoid

- Do not clutter this directory again with large generated artifacts unless they are actively being used.
- Do not overwrite confirmed mappings with weaker heuristic output.
- Do not assume IRS PDFs expose clean semantic labels internally; they often do not.
- Do not assume checkboxes can be resolved from field names alone; visual confirmation is often needed.

## If You Need To Resume Quickly

Start here:

1. `README.md`
2. `STRATEGIES.md`
3. `f1120-field-map-review.md`
4. `map_1120_fields.py`

That should be enough for a future agent to continue productively without redoing the entire investigation.
