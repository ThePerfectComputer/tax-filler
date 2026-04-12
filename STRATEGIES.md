# Strategies

This document describes strategies an agent can use to extract, learn, verify, and fill fields in a fillable tax PDF such as IRS Form 1120.

## 1. Direct AcroForm Introspection

Use a PDF library to inspect the PDF form structure directly.

Useful for:

- raw field names
- field types
- page/widget rectangles
- existing field values

Typical tools:

- `pypdf`
- `PyMuPDF`

Strengths:

- precise field ids
- robust for filling
- no OCR required

Weaknesses:

- field labels are often not stored in a friendly way
- internal names can be ugly and not human-meaningful

This project already uses this strategy.

## 2. Geometry Matching Between Widgets and Nearby Text

Extract:

- widget bounding boxes
- page text with coordinates

Then score nearby text as likely labels using heuristics such as:

- text above the field
- text to the left of the field
- text to the right of checkboxes
- overlap, distance, and alignment

Strengths:

- fully automatic
- works well on structured forms
- avoids OCR when the PDF text layer is good

Weaknesses:

- can confuse nearby rows in dense tables
- can grab instructions or neighboring prompts

This project already uses this strategy.

## 3. Page-Specific Structural Overrides

When a form has rigid layout patterns, use page-specific knowledge instead of relying purely on general heuristics.

Examples:

- page 1 income and deduction rows
- page 4 Schedule K table columns
- page 6 Schedule L row/column grids

Strengths:

- much more reliable for repeated table layouts
- easy to reason about
- very good for IRS forms that barely change year to year

Weaknesses:

- less portable across unrelated forms
- must be updated if the IRS layout changes materially

This project already uses this strategy.

## 4. Human-in-the-Loop Probe Filling

Generate a review PDF where uncertain fields are filled with unique markers like:

- `LC01_001`
- `LC04_027`

Then ask a human where each marker appears.

For checkboxes, toggle them on and ask which prompt they correspond to.

Strengths:

- excellent for resolving the last ambiguous fields
- fast when screenshots or crop batches are available
- creates hard confirmations instead of probabilistic guesses

Weaknesses:

- requires human review
- should be reserved for ambiguous cases, not everything

This project already uses this strategy.

## 5. Rendered Image Inspection

Render PDF pages to images and inspect the result directly.

Possible uses:

- visually confirm probe markers
- inspect dense layouts
- produce screenshot crops for human review

Possible tools:

- `PyMuPDF`
- `Pillow`
- the agent's image inspection capability

Strengths:

- matches what a human actually sees
- very useful for debugging layout issues

Weaknesses:

- not enough by itself unless paired with markers or OCR

This project already used this for review/debugging.

## 6. Localized Probe, Render, Crop, Inspect

This is a composable tactic, not a hard-coded end-to-end workflow.

An agent can use it whenever another strategy leaves ambiguity behind.

Typical loop:

1. pick a target field
2. write a distinctive probe value into that field
3. render the relevant PDF page
4. crop around the expected visual region
5. inspect the crop visually and/or with OCR
6. infer what visible prompt or table slot the field corresponds to
7. write the result back into the field map

For text fields:

- write a unique marker such as `LC04_031`
- render the page
- locate the marker visually
- read the nearby label or row/column meaning

For checkboxes:

- toggle the checkbox on
- render the page
- crop the checkbox region
- inspect which visible yes/no prompt or sub-question was activated

This tactic combines well with:

- direct AcroForm introspection
- geometry matching
- page-specific structural rules
- human-in-the-loop confirmation
- OCR fallback

Strengths:

- useful when the PDF text layer is ambiguous
- especially good for checkboxes
- lets the agent validate what a human viewer would actually see
- can be applied narrowly to only the unresolved fields

Weaknesses:

- slower than pure geometry extraction
- requires rendering infrastructure
- visual interpretation can still be ambiguous in dense layouts

This project already used pieces of this tactic through probe PDFs, rendered crops, and manual screenshot confirmation.

## 7. OCR as a Fallback

Render a page or crop, then use OCR to read nearby text.

Possible tools:

- `tesseract`
- `pytesseract`

Strengths:

- useful when PDF text extraction is unreliable
- useful on scans or partially rasterized PDFs

Weaknesses:

- often noisy
- can introduce spacing and punctuation errors
- slower than native PDF text extraction

This project used OCR only as a secondary tie-breaker, not as the primary strategy.

## 8. Canonical Schema Layer

Do not force downstream callers to use raw PDF field ids.

Instead, define a stable schema such as:

```json
{
  "company": {
    "name": "...",
    "ein": "..."
  },
  "income": {
    "gross_receipts": 0
  }
}
```

Then compile that schema into PDF fields.

Strengths:

- cleaner API
- easier automation
- safer against future changes in raw field names

Weaknesses:

- requires a careful mapping layer
- more design work up front

This project has not fully implemented this yet, but it is the recommended next step.

## 9. Confidence Tracking and Review Queues

Every field extraction should carry confidence metadata.

Use that to:

- generate a review list
- decide when to auto-accept vs escalate
- focus human effort on the smallest set of unresolved fields

Strengths:

- keeps review efficient
- makes progress measurable

Weaknesses:

- heuristic confidence is not the same as truth

This project already uses this strategy.

## 10. Recommended Workflow For Future Agents

1. Inspect the PDF form structure directly.
2. Build an initial geometry-based field map.
3. Add page-specific structural logic for rigid sections.
4. Write the current field map and a low-confidence review list.
5. For unresolved fields, use probe values and, when helpful, render/crop/inspect locally.
6. Generate probe PDFs with unique markers when human review is useful.
7. Incorporate human-confirmed results as hard overrides.
8. Expose filling through a friendly JSON-based interface.
9. Keep generated artifacts disposable and regenerate them as needed.

## 11. What Worked Best So Far

The most effective combination in this project was:

1. direct field extraction
2. geometry-based label matching
3. page-specific overrides
4. localized probe/render/crop/inspect on ambiguous regions
5. human-confirmed probe markers for the last ambiguous fields

That combination got most of the form into a high-confidence state without requiring full manual mapping from scratch.
