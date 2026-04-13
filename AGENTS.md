# AGENTS.md

This directory is the beginning of a standalone Form 1120 PDF-filling project.

The immediate goal is:

1. support filling Form 1120 from human-readable JSON
2. expand year-specific friendly-schema coverage for 2024 and 2025
3. keep exploratory reverse-engineering tools available for unresolved sections

## Directory Intent

Treat this directory as an emerging repo boundary.

Keep it focused on:

- source PDFs
- JSON-to-PDF filling logic
- friendly-schema logic
- field extraction and mapping logic when needed
- review/probe generation logic
- project documentation

Avoid dumping regenerated output PDFs, screenshots, or other bulky scratch artifacts here long-term unless they are needed for debugging in the current session.

## Current Important Files

- `forms/f1120_2025.pdf`
  - Official IRS fillable PDF currently used as the main source form for mapping work.

- `forms/f1120_2024.pdf`
  - Official IRS fillable PDF used for the year-specific friendly filler flow.

- `srcs/fill_pdf_from_json.py`
  - Fills the PDF from JSON values.
  - Accepts the year-specific friendly schemas.

- `srcs/friendly_1120_2024.py`
  - 2024-specific friendly schema mapper.

- `srcs/friendly_1120_2025.py`
  - 2025-specific friendly schema mapper.

- `srcs/friendly_1120_shared.py`
  - Shared helpers for the friendly schema layer.

- `srcs/generate_low_confidence_probe.py`
  - Generates probe values for unresolved fields so they can be visually confirmed.

- `srcs/map_1120_fields.py`
  - Exploratory field-mapping script used when expanding coverage into still-unmapped sections.

- `README.md`
  - Current project status and unresolved field summary.

- `STRATEGIES.md`
  - Extraction and validation strategies used so far and recommended going forward.

## What Has Already Been Learned

Several fields that were originally ambiguous have already been confirmed manually using:

- unique text probes
- rendered PDF screenshots
- human review of screenshots

Those confirmations were baked back into the current code and reverse-engineering notes.

Do not throw those away by replacing confirmed overrides with lower-confidence heuristic guesses.

## Current Remaining Coverage Gaps

As of the latest verification pass, the biggest uncovered areas for the friendly schema are concentrated in:

1. Page 2 Schedule C
   - essentially the full page is still outside the friendly schema

2. Page 4 Schedule K
   - accounting-method controls, ownership tables, and several yes/no prompts

3. Page 6
   - Schedule L, Schedule M-1, and Schedule M-2 are largely uncovered in the friendly schema

## Recommended Working Style

When continuing this project:

1. Inspect the year-specific friendly schema before making major conclusions:

```bash
cd taxes/tax-filler
sed -n '1,260p' srcs/friendly_1120_2024.py
sed -n '1,260p' srcs/friendly_1120_2025.py
```

2. If deeper reverse-engineering is needed, regenerate the current map:

```bash
cd taxes/tax-filler
python3 srcs/map_1120_fields.py
```

3. If needed, generate a fresh probe package:

```bash
cd taxes/tax-filler
python3 srcs/generate_low_confidence_probe.py
```

4. Prefer composable strategies:
   - geometry matching
   - page-specific structural rules
   - localized probe/render/crop/inspect
   - OCR fallback
   - human confirmation only where ambiguity remains

5. After confirming fields, add them to the appropriate friendly year module and verify by producing a filled PDF from an example JSON.

## Filling Workflow

Current filler command:

```bash
cd taxes/tax-filler
python3 srcs/fill_pdf_from_json.py \
  --pdf forms/f1120_2025.pdf \
  --values examples/example-1120-friendly-2025.json \
  --output output.pdf
```

And for 2024:

```bash
cd taxes/tax-filler
python3 srcs/fill_pdf_from_json.py \
  --pdf forms/f1120_2024.pdf \
  --values examples/example-1120-friendly-2024.json \
  --output output-2024.pdf
```

## Near-Term Next Steps

The most useful next steps are:

1. finish resolving the remaining low-confidence fields
2. improve coverage on page 2, page 4, and page 6 for the 2024 form
3. keep the 2024 and 2025 schemas aligned where practical
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
3. `srcs/friendly_1120_2024.py`
4. `srcs/friendly_1120_2025.py`

That should be enough for a future agent to continue productively without redoing the entire investigation.
