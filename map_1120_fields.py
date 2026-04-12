from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import fitz
from PIL import Image, ImageOps

try:
    import pytesseract
except ImportError:  # pragma: no cover - optional fallback
    pytesseract = None


ROOT = Path(__file__).resolve().parent
INPUT_PDF = ROOT / "f1120.pdf"
OUTPUT_JSON = ROOT / "f1120-field-map.json"
OUTPUT_CSV = ROOT / "f1120-field-map.csv"
OUTPUT_REVIEW = ROOT / "f1120-field-map-review.md"
DEBUG_DIR = ROOT / "debug"


CONFIRMED_LABELS = {
    "topmostSubform[0].Page1[0].f1_21[0]": "6 Gross rents",
    "topmostSubform[0].Page1[0].f1_22[0]": "7 Gross royalties",
    "topmostSubform[0].Page1[0].f1_23[0]": "8 Capital gain net income (attach Schedule D (Form 1120))",
    "topmostSubform[0].Page1[0].f1_26[0]": "11 Total income. Add lines 3 through 10",
    "topmostSubform[0].Page1[0].f1_28[0]": "13 Salaries and wages (less employment credits)",
    "topmostSubform[0].Page1[0].f1_31[0]": "16 Rents",
    "topmostSubform[0].Page1[0].f1_33[0]": "18 Interest (see instructions)",
    "topmostSubform[0].Page1[0].f1_37[0]": "22 Advertising",
    "topmostSubform[0].Page1[0].f1_46[0]": "29c Add lines 29a and 29b",
    "topmostSubform[0].Page2[0].Table_ScheduleC[0].Line2[0].f2_6[0]": "Schedule C line 2 column (c) Special deductions ((a) x (b))",
    "topmostSubform[0].Page2[0].Table_ScheduleC[0].Line20[0].f2_66[0]": "Schedule C line 20 Other dividends",
    "topmostSubform[0].Page3[0].f3_1[0]": "Schedule J line 1a Income tax (see instructions)",
    "topmostSubform[0].Page3[0].f3_2[0]": "Schedule J line 1b Tax from Form 1120-L (see instructions)",
    "topmostSubform[0].Page3[0].f3_3[0]": "Schedule J line 1c Section 1291 tax from Form 8621",
    "topmostSubform[0].Page3[0].f3_4[0]": "Schedule J line 1d Tax adjustment from Form 8978",
    "topmostSubform[0].Page3[0].f3_5[0]": "Schedule J line 1e Additional tax under section 197(f)",
    "topmostSubform[0].Page3[0].f3_8[0]": "Schedule J line 1z Other chapter 1 tax",
    "topmostSubform[0].Page3[0].f3_38[0]": "Schedule J line 17 Tax deposited with Form 7004",
    "topmostSubform[0].Page3[0].f3_40[0]": "Schedule J line 19 Total payments. Combine lines 13 through 18",
    "topmostSubform[0].Page3[0].Line20_ReadOrder[0].f3_41[0]": "Schedule J line 20a Form 2439",
    "topmostSubform[0].Page4[0].f4_3[0]": "Schedule K line 2b Business activity",
    "topmostSubform[0].Page4[0].f4_4[0]": "Schedule K line 2c Product or service",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row1[0].f4_8[0]": "Schedule K line 5a table row 1 - Country of incorporation",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row1[0].f4_9[0]": "Schedule K line 5a table row 1 - Maximum percentage owned in voting stock",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row2[0].f4_10[0]": "Schedule K line 5a table row 2 - Name of corporation",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row2[0].f4_11[0]": "Schedule K line 5a table row 2 - Employer identification number (if any)",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row2[0].f4_12[0]": "Schedule K line 5a table row 2 - Country of incorporation",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row2[0].f4_13[0]": "Schedule K line 5a table row 2 - Maximum percentage owned in voting stock",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row3[0].f4_14[0]": "Schedule K line 5a table row 3 - Name of corporation",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row3[0].f4_15[0]": "Schedule K line 5a table row 3 - Employer identification number (if any)",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row3[0].f4_16[0]": "Schedule K line 5a table row 3 - Country of incorporation",
    "topmostSubform[0].Page4[0].Table_Line5a[0].Row3[0].f4_17[0]": "Schedule K line 5a table row 3 - Maximum percentage owned in voting stock",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row1[0].f4_20[0]": "Schedule K line 5b table row 1 - Country of organization",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row1[0].f4_21[0]": "Schedule K line 5b table row 1 - Maximum percentage owned in profit, loss, or capital",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row2[0].f4_22[0]": "Schedule K line 5b table row 2 - Name of entity",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row2[0].f4_23[0]": "Schedule K line 5b table row 2 - Employer identification number (if any)",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row2[0].f4_24[0]": "Schedule K line 5b table row 2 - Country of organization",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row2[0].f4_25[0]": "Schedule K line 5b table row 2 - Maximum percentage owned in profit, loss, or capital",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row3[0].f4_26[0]": "Schedule K line 5b table row 3 - Name of entity",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row3[0].f4_27[0]": "Schedule K line 5b table row 3 - Employer identification number (if any)",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row3[0].f4_28[0]": "Schedule K line 5b table row 3 - Country of organization",
    "topmostSubform[0].Page4[0].Table_Line5b[0].Row3[0].f4_29[0]": "Schedule K line 5b table row 3 - Maximum percentage owned in profit, loss, or capital",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line2b[0].f6_12[0]": "Schedule L line 2b Less allowance for bad debts - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line3[0].f6_13[0]": "Schedule L line 3 Inventories - Beginning of tax year (a)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line3[0].f6_14[0]": "Schedule L line 3 Inventories - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line3[0].f6_15[0]": "Schedule L line 3 Inventories - End of tax year (c)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line3[0].f6_16[0]": "Schedule L line 3 Inventories - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line4[0].f6_17[0]": "Schedule L line 4 U.S. government obligations - Beginning of tax year (a)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line4[0].f6_18[0]": "Schedule L line 4 U.S. government obligations - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line4[0].f6_19[0]": "Schedule L line 4 U.S. government obligations - End of tax year (c)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line4[0].f6_20[0]": "Schedule L line 4 U.S. government obligations - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line5[0].f6_21[0]": "Schedule L line 5 Tax-exempt securities - Beginning of tax year (a)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line5[0].f6_22[0]": "Schedule L line 5 Tax-exempt securities - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line5[0].f6_23[0]": "Schedule L line 5 Tax-exempt securities - End of tax year (c)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line5[0].f6_24[0]": "Schedule L line 5 Tax-exempt securities - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line6[0].f6_27[0]": "Schedule L line 6 Other current assets (attach statement) - End of tax year (c)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line6[0].f6_28[0]": "Schedule L line 6 Other current assets (attach statement) - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line7[0].f6_29[0]": "Schedule L line 7 Loans to shareholders - Beginning of tax year (a)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line7[0].f6_30[0]": "Schedule L line 7 Loans to shareholders - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line7[0].f6_31[0]": "Schedule L line 7 Loans to shareholders - End of tax year (c)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line7[0].f6_32[0]": "Schedule L line 7 Loans to shareholders - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line8[0].f6_33[0]": "Schedule L line 8 Mortgage and real estate loans - Beginning of tax year (a)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line8[0].f6_34[0]": "Schedule L line 8 Mortgage and real estate loans - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line8[0].f6_35[0]": "Schedule L line 8 Mortgage and real estate loans - End of tax year (c)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line8[0].f6_36[0]": "Schedule L line 8 Mortgage and real estate loans - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line9[0].f6_37[0]": "Schedule L line 9 Other investments (attach statement) - Beginning of tax year (a)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line9[0].f6_38[0]": "Schedule L line 9 Other investments (attach statement) - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line9[0].f6_39[0]": "Schedule L line 9 Other investments (attach statement) - End of tax year (c)",
    "topmostSubform[0].Page6[0].Table_SchL_Assets[0].Line9[0].f6_40[0]": "Schedule L line 9 Other investments (attach statement) - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line16[0].f6_80[0]": "Schedule L line 16 Accounts payable - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line17[0].f6_82[0]": "Schedule L line 17 Mortgages, notes, bonds payable in less than 1 year - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line17[0].f6_84[0]": "Schedule L line 17 Mortgages, notes, bonds payable in less than 1 year - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line19[0].f6_92[0]": "Schedule L line 19 Loans from shareholders - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line20[0].f6_94[0]": "Schedule L line 20 Mortgages, notes, bonds payable in 1 year or more - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line20[0].f6_96[0]": "Schedule L line 20 Mortgages, notes, bonds payable in 1 year or more - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line22a[0].f6_104[0]": "Schedule L line 22a Capital stock - Preferred stock - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line24[0].f6_114[0]": "Schedule L line 24 Retained earnings - Appropriated (attach statement) - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line24[0].f6_115[0]": "Schedule L line 24 Retained earnings - Appropriated (attach statement) - End of tax year (c)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line24[0].f6_116[0]": "Schedule L line 24 Retained earnings - Appropriated (attach statement) - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line25[0].f6_120[0]": "Schedule L line 25 Retained earnings - Unappropriated - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line27[0].f6_128[0]": "Schedule L line 27 Less cost of treasury stock - End of tax year (d)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line28[0].f6_129[0]": "Schedule L line 28 Total liabilities and shareholders' equity - Beginning of tax year (a)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line28[0].f6_130[0]": "Schedule L line 28 Total liabilities and shareholders' equity - Beginning of tax year (b)",
    "topmostSubform[0].Page6[0].Table_SchL_Liabilities[0].Line28[0].f6_131[0]": "Schedule L line 28 Total liabilities and shareholders' equity - End of tax year (c)",
    "topmostSubform[0].Page6[0].SchM-1_Right[0].f6_148[0]": "Schedule M-1 line 4 Income subject to tax not recorded on books this year (itemize) - amount",
}


@dataclass
class Line:
    page_index: int
    text: str
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2


@dataclass
class Candidate:
    text: str
    mode: str
    score: float
    gap_x: float
    gap_y: float


def normalize_label(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.strip(". ")
    return text


def line_groups(page: fitz.Page, page_index: int) -> list[Line]:
    words = []
    for x0, y0, x1, y1, text, _block_no, _line_no, _word_no in page.get_text("words"):
        text = normalize_label(text)
        if not text:
            continue
        words.append((x0, y0, x1, y1, text))

    words.sort(key=lambda item: ((item[1] + item[3]) / 2, item[0]))
    rows: list[list[tuple[float, float, float, float, str]]] = []
    for word in words:
        cy = (word[1] + word[3]) / 2
        if not rows:
            rows.append([word])
            continue
        prev_row = rows[-1]
        prev_cy = sum((item[1] + item[3]) / 2 for item in prev_row) / len(prev_row)
        if abs(cy - prev_cy) <= 2.5:
            prev_row.append(word)
        else:
            rows.append([word])

    chunks: list[Line] = []
    for row in rows:
        row.sort(key=lambda item: item[0])
        current = [row[0]]
        for word in row[1:]:
            gap = word[0] - current[-1][2]
            if gap <= 12:
                current.append(word)
                continue
            chunks.append(chunk_to_line(current, page_index))
            current = [word]
        if current:
            chunks.append(chunk_to_line(current, page_index))

    chunks = [chunk for chunk in chunks if chunk is not None]
    chunks.sort(key=lambda line: (line.y0, line.x0))
    return chunks


def chunk_to_line(words: list[tuple[float, float, float, float, str]], page_index: int) -> Line | None:
    text = normalize_label(" ".join(word[4] for word in words))
    text = re.sub(r"(?:\s*\.\s*){2,}", " ", text)
    text = normalize_label(text)
    if not text:
        return None
    if re.fullmatch(r"[\d$(),.-]+", text):
        return None
    x0 = min(word[0] for word in words)
    y0 = min(word[1] for word in words)
    x1 = max(word[2] for word in words)
    y1 = max(word[3] for word in words)
    return Line(page_index=page_index, text=text, x0=x0, y0=y0, x1=x1, y1=y1)


def merge_lines(a: Line, b: Line) -> Line:
    return Line(
        page_index=a.page_index,
        text=normalize_label(f"{a.text} {b.text}"),
        x0=min(a.x0, b.x0),
        y0=min(a.y0, b.y0),
        x1=max(a.x1, b.x1),
        y1=max(a.y1, b.y1),
    )


def render_page_image(page: fitz.Page, scale: float = 4.0) -> Image.Image:
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return ImageOps.grayscale(image)


def ocr_candidate_for_widget(widget: fitz.Widget, page_image: Image.Image, scale: float = 4.0) -> Candidate | None:
    if pytesseract is None:
        return None

    rect = widget.rect
    crop_box = None
    if widget.field_type_string == "CheckBox" and rect.x0 < 140 and rect.y1 < 180:
        crop_box = (
            0,
            max(0, int((rect.y0 - 12) * scale)),
            min(page_image.width, int((rect.x0 + 110) * scale)),
            min(page_image.height, int((rect.y1 + 22) * scale)),
        )
    elif widget.field_type_string == "Text" and rect.x0 > 350 and 145 < rect.y0 < 260:
        crop_box = (
            max(0, int((rect.x0 - 380) * scale)),
            max(0, int((rect.y0 - 14) * scale)),
            min(page_image.width, int((rect.x1 + 18) * scale)),
            min(page_image.height, int((rect.y1 + 22) * scale)),
        )

    if crop_box is None or crop_box[2] <= crop_box[0] or crop_box[3] <= crop_box[1]:
        return None

    crop = ImageOps.autocontrast(page_image.crop(crop_box))
    data = pytesseract.image_to_data(crop, config="--psm 6", output_type=pytesseract.Output.DICT)
    grouped: dict[tuple[int, int, int], list[tuple[int, int, int, int, str]]] = defaultdict(list)
    for i, text in enumerate(data["text"]):
        text = normalize_label(text)
        if not text:
            continue
        conf = int(data["conf"][i]) if str(data["conf"][i]).strip() not in {"", "-1"} else -1
        if conf < 0:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        grouped[key].append((data["left"][i], data["top"][i], data["width"][i], data["height"][i], text))

    if not grouped:
        return None

    lines: list[tuple[str, float]] = []
    for words in grouped.values():
        words.sort(key=lambda item: item[0])
        text = normalize_label(" ".join(word[4] for word in words))
        if not text:
            continue
        if text in {"LJ", "LI", "[]", "|", "_"}:
            continue
        top = min(word[1] for word in words)
        bottom = max(word[1] + word[3] for word in words)
        center_y = (top + bottom) / 2
        lines.append((text, center_y))

    if not lines:
        return None

    widget_center_y = ((rect.y0 + rect.y1) / 2) * scale - crop_box[1]
    lines.sort(key=lambda item: abs(item[1] - widget_center_y))
    text, center_y = lines[0]

    for extra_text, extra_center_y in lines[1:3]:
        is_continuation = not re.match(r"^[0-9]+[a-z]?\b", extra_text.lower()) and not re.match(r"^[A-Z]\b", extra_text)
        if 0 < extra_center_y - center_y <= 34 and is_continuation:
            text = normalize_label(f"{text} {extra_text}")
            break

    distance = abs(center_y - widget_center_y) / scale
    score = max(0.0, 120.0 - distance * 5.0)
    text = re.sub(r"\s*[|_]+\s*", " ", text)
    text = normalize_label(text)
    return Candidate(text=text, mode="ocr", score=score, gap_x=0.0, gap_y=distance)


def overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def score_candidate(widget: fitz.Widget, line: Line, mode: str) -> Candidate | None:
    rect = widget.rect
    horizontal_overlap = overlap(rect.x0, rect.x1, line.x0, line.x1)
    vertical_overlap = overlap(rect.y0, rect.y1, line.y0, line.y1)
    vertical_center_gap = abs(((rect.y0 + rect.y1) / 2) - line.center_y)
    horizontal_center_gap = abs(((rect.x0 + rect.x1) / 2) - line.center_x)
    instruction_penalty = 0.0
    if any(token in line.text.lower() for token in ("www.irs.gov", "instructions", "cat. no", "department of the treasury")):
        instruction_penalty += 18
    if len(line.text) > 45:
        instruction_penalty += min(18, (len(line.text) - 45) * 0.45)
    if re.fullmatch(r"\d+[a-z]?", line.text.lower()):
        instruction_penalty += 35
    if re.fullmatch(r"\(\d+\)", line.text):
        instruction_penalty += 40
    if line.text == "$":
        instruction_penalty += 30
    if widget.field_type_string == "CheckBox" and line.text.startswith("("):
        instruction_penalty += 18
    label_bonus = 0.0
    if re.search(r"[A-Za-z]{3,}", line.text):
        label_bonus += 5
    if re.match(r"^[0-9]+[a-z]?\b", line.text.lower()):
        label_bonus += 8
    if len(line.text.split()) >= 3:
        label_bonus += 12
    if widget.field_type_string == "Text" and line.text.lower() in {"name", "city or town", "state or province", "country"}:
        label_bonus += 8
    if mode == "above" and len(line.text) <= 22 and line.x0 <= rect.x0 + 4:
        label_bonus += 18
    if mode == "left" and rect.width > 160 and re.match(r"^[0-9]+[a-z]?\b", line.text.lower()):
        instruction_penalty += 18
    if re.match(r"^[0-9]+[a-z]?\s+[A-Za-z]", line.text):
        label_bonus += 10
    if widget.field_type_string == "CheckBox" and re.match(r"^[0-9]+[a-z]?\s+[A-Za-z]", line.text):
        label_bonus += 12
    if rect.y0 < 110 and mode == "above" and len(line.text) <= 12:
        label_bonus += 25
    if rect.x0 > 350 and rect.y0 > 150:
        if mode == "above":
            instruction_penalty += 50
        if mode == "left" and len(line.text) > 6:
            label_bonus += 28
    if rect.width > 250 and rect.y0 < 100:
        if mode == "above" and line.text.lower() == "name":
            label_bonus += 80
        if mode == "left":
            instruction_penalty += 25

    if mode == "left":
        if line.x1 > rect.x0 + 8:
            return None
        gap_x = rect.x0 - line.x1
        max_gap = 280
        if rect.x0 > 450 and rect.y0 > 160:
            max_gap = 360
        if gap_x > max_gap or vertical_center_gap > 16:
            return None
        score = 106 - gap_x * 0.22 - vertical_center_gap * 2.6 + vertical_overlap * 1.5 + label_bonus - instruction_penalty
    elif mode == "right":
        if line.x0 < rect.x1 - 8:
            return None
        gap_x = line.x0 - rect.x1
        if gap_x > 140 or vertical_center_gap > 15:
            return None
        score = 98 - gap_x * 0.7 - vertical_center_gap * 2.5 + vertical_overlap * 1.5 + label_bonus - instruction_penalty
    elif mode == "above":
        if line.y1 > rect.y0 + 5:
            return None
        gap_y = rect.y0 - line.y1
        if gap_y > 30:
            return None
        if horizontal_overlap <= 0 and horizontal_center_gap > rect.width * 0.9:
            return None
        score = 96 - gap_y * 2.2 - horizontal_center_gap * 0.18 + horizontal_overlap * 0.16 + label_bonus - instruction_penalty
        gap_x = horizontal_center_gap
        return Candidate(text=line.text, mode=mode, score=score, gap_x=gap_x, gap_y=gap_y)
    else:
        return None

    return Candidate(text=line.text, mode=mode, score=score, gap_x=gap_x, gap_y=vertical_center_gap)


def merge_multiline(lines: list[Line]) -> list[Line]:
    merged: list[Line] = []
    idx = 0
    while idx < len(lines):
        current = lines[idx]
        text_parts = [current.text]
        x0, y0, x1, y1 = current.x0, current.y0, current.x1, current.y1
        j = idx + 1
        while j < len(lines):
            nxt = lines[j]
            aligned = abs(nxt.x0 - current.x0) < 12
            close = 0 <= nxt.y0 - y1 <= 8
            similar_width = abs((nxt.x1 - nxt.x0) - (current.x1 - current.x0)) < 80
            continuation = nxt.text.startswith("(") or current.text.endswith(":")
            new_item = re.match(r"^[0-9]+[a-z]?\s+[A-Za-z]", nxt.text)
            if new_item and not nxt.text.startswith("("):
                similar_width = False
            if aligned and close and (similar_width or continuation):
                text_parts.append(nxt.text)
                x0, y0 = min(x0, nxt.x0), min(y0, nxt.y0)
                x1, y1 = max(x1, nxt.x1), max(y1, nxt.y1)
                j += 1
                current = nxt
                continue
            break
        merged.append(Line(page_index=lines[idx].page_index, text=normalize_label(" ".join(text_parts)), x0=x0, y0=y0, x1=x1, y1=y1))
        idx = j
    return merge_row_fragments(merged)


def merge_row_fragments(lines: list[Line]) -> list[Line]:
    combined: list[Line] = []
    idx = 0
    while idx < len(lines):
        current = lines[idx]
        if idx + 1 < len(lines):
            nxt = lines[idx + 1]
            same_page = current.page_index == nxt.page_index
            same_row = abs(current.center_y - nxt.center_y) <= 2.5
            small_gap = 0 <= nxt.x0 - current.x1 <= 18
            row_code = re.fullmatch(r"[0-9]+[a-z]?", current.text.lower()) or re.fullmatch(r"[a-z]", current.text.lower())
            textish = re.search(r"[A-Za-z]{3,}", nxt.text) is not None
            if same_page and same_row and small_gap and row_code and textish:
                current = merge_lines(current, nxt)
                idx += 1
        combined.append(current)
        idx += 1
    return combined


def candidates_for_widget(widget: fitz.Widget, lines: list[Line], page_image: Image.Image | None) -> list[Candidate]:
    modes = ["left", "above", "right"]
    if widget.field_type_string == "CheckBox":
        modes = ["left", "right", "above"]

    candidates: list[Candidate] = []
    for line in lines:
        for mode in modes:
            candidate = score_candidate(widget, line, mode)
            if candidate is not None:
                candidates.append(candidate)

    ocr_candidate = ocr_candidate_for_widget(widget, page_image) if page_image is not None else None
    if ocr_candidate is not None:
        candidates.append(ocr_candidate)

    deduped: dict[tuple[str, str], Candidate] = {}
    for candidate in candidates:
        key = (candidate.text, candidate.mode)
        if key not in deduped or candidate.score > deduped[key].score:
            deduped[key] = candidate

    return sorted(deduped.values(), key=lambda item: item.score, reverse=True)


def short_field_name(field_name: str) -> str:
    parts = field_name.split(".")
    return parts[-1]


def annotate_page(page: fitz.Page, page_rows: list[dict], out_path: Path) -> None:
    debug = page.parent.load_page(page.number)
    for row in page_rows[:25]:
        rect = fitz.Rect(row["rect"])
        debug.draw_rect(rect, color=(1, 0, 0), width=0.8)
        label = f"{short_field_name(row['field_name'])}: {row['label'][:40]}"
        debug.insert_text((rect.x0, max(10, rect.y0 - 3)), label, fontsize=6, color=(0, 0, 1))
    pix = debug.get_pixmap(dpi=170, alpha=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(out_path)


def page1_income_labels(page: fitz.Page) -> list[Line]:
    raw_lines = line_groups(page, 0)
    labels = [
        line
        for line in raw_lines
        if 155 <= line.y0 <= 520
        and 55 <= line.x0 <= 260
        and not line.text.startswith(("Income", "Deductions", "Refundable credits"))
    ]
    normalized: list[Line] = []
    current_numeric = "1"
    next_numeric = 2
    for line in labels:
        text = line.text
        if text.startswith("1a "):
            current_numeric = "1"
        elif re.match(r"^[bc]\b", text.lower()):
            text = f"{current_numeric}{text}"
        elif not re.match(r"^[0-9]+[a-z]?\b", text.lower()):
            text = f"{next_numeric} {text}"
            next_numeric += 1
        normalized.append(Line(page_index=line.page_index, text=text, x0=line.x0, y0=line.y0, x1=line.x1, y1=line.y1))
    return normalized


def page1_overrides(page: fitz.Page) -> dict[str, str]:
    overrides: dict[str, str] = {
        "topmostSubform[0].Page1[0].PgHeader[0].f1_1[0]": "Tax year beginning",
        "topmostSubform[0].Page1[0].PgHeader[0].f1_2[0]": "Tax year ending month and day",
        "topmostSubform[0].Page1[0].PgHeader[0].f1_3[0]": "Tax year ending year",
        "topmostSubform[0].Page1[0].NameFieldsReadOrder[0].f1_4[0]": "Name",
        "topmostSubform[0].Page1[0].NameFieldsReadOrder[0].f1_5[0]": "Number and street. If a P.O. box, see instructions",
        "topmostSubform[0].Page1[0].NameFieldsReadOrder[0].f1_6[0]": "Room or suite no.",
        "topmostSubform[0].Page1[0].NameFieldsReadOrder[0].f1_7[0]": "City or town",
        "topmostSubform[0].Page1[0].NameFieldsReadOrder[0].f1_8[0]": "State or province",
        "topmostSubform[0].Page1[0].NameFieldsReadOrder[0].f1_9[0]": "Country",
        "topmostSubform[0].Page1[0].NameFieldsReadOrder[0].f1_10[0]": "ZIP or foreign postal code",
        "topmostSubform[0].Page1[0].f1_11[0]": "B Employer identification number",
        "topmostSubform[0].Page1[0].f1_12[0]": "C Date incorporated",
        "topmostSubform[0].Page1[0].f1_13[0]": "D Total assets (see instructions)",
    }
    widgets = list(page.widgets())

    a_fields = [w for w in widgets if ".A_ReadOrder[0].c1_" in w.field_name]
    a_fields.sort(key=lambda widget: widget.rect.y0)
    a_labels = [
        "1a Consolidated return (attach Form 851)",
        "1b Life/nonlife consolidated return",
        "2 Personal holding co. (attach Sch. PH)",
        "3 Personal service corp. (see instructions)",
        "4 Schedule M-3 attached",
    ]
    for widget, label in zip(a_fields[:5], a_labels):
        overrides[widget.field_name] = label

    e_fields = [w for w in widgets if re.search(r"\.c1_[6-9]\[0\]$", w.field_name)]
    e_fields.sort(key=lambda widget: widget.rect.x0)
    e_labels = ["Initial return", "Final return", "Name change", "Address change"]
    for widget, label in zip(e_fields, e_labels):
        overrides[widget.field_name] = label

    income_fields = [
        w
        for w in widgets
        if w.field_type_string == "Text"
        and w.rect.x0 > 390
        and 150 <= w.rect.y0 <= 520
        and w.rect.width > 50
    ]
    income_fields.sort(key=lambda widget: widget.rect.y0)
    labels = page1_income_labels(page)
    for widget in income_fields:
        widget_center = (widget.rect.y0 + widget.rect.y1) / 2
        nearest = min(labels, key=lambda line: abs(line.center_y - widget_center))
        overrides[widget.field_name] = nearest.text

    return overrides


def page4_overrides(page: fitz.Page) -> dict[str, str]:
    overrides: dict[str, str] = {}

    explicit = {
        "topmostSubform[0].Page4[0].c4_1[0]": "Schedule K line 1a Accounting method - Cash",
        "topmostSubform[0].Page4[0].c4_1[1]": "Schedule K line 1b Accounting method - Accrual",
        "topmostSubform[0].Page4[0].c4_1[2]": "Schedule K line 1c Accounting method - Other",
        "topmostSubform[0].Page4[0].f4_1[0]": "Schedule K line 1c Other accounting method (specify)",
        "topmostSubform[0].Page4[0].f4_2[0]": "Schedule K line 2a Business activity code no.",
        "topmostSubform[0].Page4[0].f4_3[0]": "Schedule K line 2b Business activity",
        "topmostSubform[0].Page4[0].f4_4[0]": "Schedule K line 2c Product or service",
        "topmostSubform[0].Page4[0].c4_2[0]": "Schedule K line 3 Yes",
        "topmostSubform[0].Page4[0].c4_2[1]": "Schedule K line 3 No",
        "topmostSubform[0].Page4[0].f4_5[0]": "Schedule K line 3 If Yes - parent corporation name and EIN",
        "topmostSubform[0].Page4[0].c4_3[0]": "Schedule K line 4a Yes",
        "topmostSubform[0].Page4[0].c4_3[1]": "Schedule K line 4a No",
        "topmostSubform[0].Page4[0].c4_4[0]": "Schedule K line 4b Yes",
        "topmostSubform[0].Page4[0].c4_4[1]": "Schedule K line 4b No",
        "topmostSubform[0].Page4[0].c4_5[0]": "Schedule K line 5a Yes",
        "topmostSubform[0].Page4[0].c4_5[1]": "Schedule K line 5a No",
        "topmostSubform[0].Page4[0].c4_6[0]": "Schedule K line 5b Yes",
        "topmostSubform[0].Page4[0].c4_6[1]": "Schedule K line 5b No",
        "topmostSubform[0].Page4[0].c4_7[0]": "Schedule K line 6 Yes",
        "topmostSubform[0].Page4[0].c4_7[1]": "Schedule K line 6 No",
        "topmostSubform[0].Page4[0].c4_8[0]": "Schedule K line 7 Yes",
        "topmostSubform[0].Page4[0].c4_8[1]": "Schedule K line 7 No",
        "topmostSubform[0].Page4[0].f4_31[0]": "Schedule K line 7a Percentage owned",
        "topmostSubform[0].Page4[0].f4_32[0]": "Schedule K line 7b Owner's country",
        "topmostSubform[0].Page4[0].f4_33[0]": "Schedule K line 7c Number of Forms 5472 attached",
        "topmostSubform[0].Page4[0].c4_9[0]": "Schedule K line 8 Publicly offered debt instruments with OID checkbox",
        "topmostSubform[0].Page4[0].f4_34[0]": "Schedule K line 9 Tax-exempt interest received or accrued",
        "topmostSubform[0].Page4[0].f4_35[0]": "Schedule K line 10 Number of shareholders at end of tax year",
        "topmostSubform[0].Page4[0].c4_10[0]": "Schedule K line 11 Elect to forego NOL carryback period checkbox",
        "topmostSubform[0].Page4[0].f4_36[0]": "Schedule K line 12 Available NOL carryover from prior tax years",
    }
    overrides.update(explicit)

    line5a_cols = {
        "f4_6[0]": "Schedule K line 5a table row 1 - Name of corporation",
        "f4_7[0]": "Schedule K line 5a table row 1 - Employer identification number (if any)",
        "f4_8[0]": "Schedule K line 5a table row 1 - Country of incorporation",
        "f4_9[0]": "Schedule K line 5a table row 1 - Maximum percentage owned in voting stock",
        "f4_10[0]": "Schedule K line 5a table row 2 - Name of corporation",
        "f4_11[0]": "Schedule K line 5a table row 2 - Employer identification number (if any)",
        "f4_12[0]": "Schedule K line 5a table row 2 - Country of incorporation",
        "f4_13[0]": "Schedule K line 5a table row 2 - Maximum percentage owned in voting stock",
        "f4_14[0]": "Schedule K line 5a table row 3 - Name of corporation",
        "f4_15[0]": "Schedule K line 5a table row 3 - Employer identification number (if any)",
        "f4_16[0]": "Schedule K line 5a table row 3 - Country of incorporation",
        "f4_17[0]": "Schedule K line 5a table row 3 - Maximum percentage owned in voting stock",
    }
    for suffix, label in line5a_cols.items():
        overrides[f"topmostSubform[0].Page4[0].Table_Line5a[0].Row{1 if 'f4_6' <= suffix <= 'f4_9' else 2 if 'f4_10' <= suffix <= 'f4_13' else 3}[0].{suffix}"] = label

    line5b_cols = {
        "f4_18[0]": "Schedule K line 5b table row 1 - Name of entity",
        "f4_19[0]": "Schedule K line 5b table row 1 - Employer identification number (if any)",
        "f4_20[0]": "Schedule K line 5b table row 1 - Country of organization",
        "f4_21[0]": "Schedule K line 5b table row 1 - Maximum percentage owned in profit, loss, or capital",
        "f4_22[0]": "Schedule K line 5b table row 2 - Name of entity",
        "f4_23[0]": "Schedule K line 5b table row 2 - Employer identification number (if any)",
        "f4_24[0]": "Schedule K line 5b table row 2 - Country of organization",
        "f4_25[0]": "Schedule K line 5b table row 2 - Maximum percentage owned in profit, loss, or capital",
        "f4_26[0]": "Schedule K line 5b table row 3 - Name of entity",
        "f4_27[0]": "Schedule K line 5b table row 3 - Employer identification number (if any)",
        "f4_28[0]": "Schedule K line 5b table row 3 - Country of organization",
        "f4_29[0]": "Schedule K line 5b table row 3 - Maximum percentage owned in profit, loss, or capital",
    }
    for suffix, label in line5b_cols.items():
        if "f4_18" <= suffix <= "f4_21":
            row = "Row1"
        elif "f4_22" <= suffix <= "f4_25":
            row = "Row2"
        else:
            row = "Row3"
        overrides[f"topmostSubform[0].Page4[0].Table_Line5b[0].{row}[0].{suffix}"] = label

    return overrides


def page6_overrides(page: fitz.Page) -> dict[str, str]:
    overrides: dict[str, str] = {}
    col_labels = {
        0: "Beginning of tax year (a)",
        1: "Beginning of tax year (b)",
        2: "End of tax year (c)",
        3: "End of tax year (d)",
    }
    sch_l_assets = {
        "Line1": "Schedule L line 1 Cash",
        "Line2a": "Schedule L line 2a Trade notes and accounts receivable",
        "Line2b": "Schedule L line 2b Less allowance for bad debts",
        "Line3": "Schedule L line 3 Inventories",
        "Line4": "Schedule L line 4 U.S. government obligations",
        "Line5": "Schedule L line 5 Tax-exempt securities",
        "Line6": "Schedule L line 6 Other current assets (attach statement)",
        "Line7": "Schedule L line 7 Loans to shareholders",
        "Line8": "Schedule L line 8 Mortgage and real estate loans",
        "Line9": "Schedule L line 9 Other investments (attach statement)",
        "Line10a": "Schedule L line 10a Buildings and other depreciable assets",
        "Line10b": "Schedule L line 10b Less accumulated depreciation",
        "Line11a": "Schedule L line 11a Depletable assets",
        "Line11b": "Schedule L line 11b Less accumulated depletion",
        "Line12": "Schedule L line 12 Land (net of any amortization)",
        "Line13a": "Schedule L line 13a Intangible assets (amortizable only)",
        "Line13b": "Schedule L line 13b Less accumulated amortization",
        "Line14": "Schedule L line 14 Other assets (attach statement)",
        "Line15": "Schedule L line 15 Total assets",
    }
    sch_l_liab = {
        "Line16": "Schedule L line 16 Accounts payable",
        "Line17": "Schedule L line 17 Mortgages, notes, bonds payable in less than 1 year",
        "Line18": "Schedule L line 18 Other current liabilities (attach statement)",
        "Line19": "Schedule L line 19 Loans from shareholders",
        "Line20": "Schedule L line 20 Mortgages, notes, bonds payable in 1 year or more",
        "Line21": "Schedule L line 21 Other liabilities (attach statement)",
        "Line22a": "Schedule L line 22a Capital stock - Preferred stock",
        "Line22b": "Schedule L line 22b Capital stock - Common stock",
        "Line23": "Schedule L line 23 Additional paid-in capital",
        "Line24": "Schedule L line 24 Retained earnings - Appropriated (attach statement)",
        "Line25": "Schedule L line 25 Retained earnings - Unappropriated",
        "Line26": "Schedule L line 26 Adjustments to shareholders' equity (attach statement)",
        "Line27": "Schedule L line 27 Less cost of treasury stock",
        "Line28": "Schedule L line 28 Total liabilities and shareholders' equity",
    }
    sch_m1 = {
        "f6_133[0]": "Schedule M-1 line 1 Net income (loss) per books",
        "f6_134[0]": "Schedule M-1 line 2 Federal income tax per books",
        "f6_135[0]": "Schedule M-1 line 3 Excess of capital losses over capital gains",
        "f6_136[0]": "Schedule M-1 line 4 Income subject to tax not recorded on books this year - description",
        "f6_137[0]": "Schedule M-1 line 4 Income subject to tax not recorded on books this year - amount",
        "f6_138[0]": "Schedule M-1 line 5 Expenses recorded on books this year not deducted on this return",
        "f6_139[0]": "Schedule M-1 line 7 Tax-exempt interest",
        "f6_140[0]": "Schedule M-1 line 8 Deductions on this return not charged against book income this year - depreciation",
        "f6_141[0]": "Schedule M-1 line 8 Deductions on this return not charged against book income this year - charitable contributions",
        "f6_142[0]": "Schedule M-1 line 8 Deductions on this return not charged against book income this year - travel and entertainment",
        "f6_143[0]": "Schedule M-1 line 9 Add lines 7 and 8",
        "f6_144[0]": "Schedule M-1 line 6 Add lines 1 through 5",
        "f6_145[0]": "Schedule M-1 line 7 Tax-exempt interest amount",
        "f6_146[0]": "Schedule M-1 line 7 Tax-exempt interest description",
        "f6_147[0]": "Schedule M-1 line 8 Deductions on this return not charged against book income this year - description",
        "f6_148[0]": "Schedule M-1 line 8 Deductions on this return not charged against book income this year - amount",
        "f6_149[0]": "Schedule M-1 line 8a Depreciation",
        "f6_150[0]": "Schedule M-1 line 8b Charitable contributions",
        "f6_151[0]": "Schedule M-1 line 8c Travel and entertainment",
        "f6_152[0]": "Schedule M-1 line 8 Other deductions amount",
        "f6_153[0]": "Schedule M-1 line 9 Add lines 7 and 8",
        "f6_154[0]": "Schedule M-1 line 10 Line 6 less line 9",
        "f6_155[0]": "Schedule M-1 line 10 Income (page 1, line 28)",
    }
    sch_m2 = {
        "f6_156[0]": "Schedule M-2 line 1 Balance at beginning of year",
        "f6_157[0]": "Schedule M-2 line 2 Net income (loss) per books",
        "f6_158[0]": "Schedule M-2 line 3 Other increases - description",
        "f6_159[0]": "Schedule M-2 line 3 Other increases - amount",
        "f6_160[0]": "Schedule M-2 line 4 Add lines 1, 2, and 3",
        "f6_161[0]": "Schedule M-2 line 6 Other decreases - description",
        "f6_162[0]": "Schedule M-2 line 4 Add lines 1, 2, and 3 amount",
        "f6_163[0]": "Schedule M-2 line 5a Distributions - Cash",
        "f6_164[0]": "Schedule M-2 line 5b Distributions - Stock",
        "f6_165[0]": "Schedule M-2 line 5c Distributions - Property",
        "f6_166[0]": "Schedule M-2 line 6 Other decreases - description",
        "f6_167[0]": "Schedule M-2 line 6 Other decreases - amount",
        "f6_168[0]": "Schedule M-2 line 7 Add lines 5 and 6",
        "f6_169[0]": "Schedule M-2 line 8 Balance at end of year (line 4 less line 7)",
    }

    for widget in page.widgets():
        name = widget.field_name
        if "Table_SchL_Assets" in name:
            match = re.search(r"Table_SchL_Assets\[0\]\.(Line[0-9ab]+)\[0\]\.f6_(\d+)\[0\]", name)
            if match:
                line_id = match.group(1)
                column_index = int(round((widget.rect.x0 - 244.8) / 82.0))
                column_index = max(0, min(3, column_index))
                overrides[name] = f"{sch_l_assets.get(line_id, line_id)} - {col_labels[column_index]}"
        elif "Table_SchL_Liabilities" in name:
            match = re.search(r"Table_SchL_Liabilities\[0\]\.(Line[0-9ab]+)\[0\]\.f6_(\d+)\[0\]", name)
            if match:
                line_id = match.group(1)
                column_index = int(round((widget.rect.x0 - 244.8) / 82.0))
                column_index = max(0, min(3, column_index))
                overrides[name] = f"{sch_l_liab.get(line_id, line_id)} - {col_labels[column_index]}"
        elif "SchM-1" in name:
            suffix = name.split(".")[-1]
            overrides[name] = sch_m1.get(suffix, f"Schedule M-1 {suffix}")
        elif "SchM-2" in name:
            suffix = name.split(".")[-1]
            overrides[name] = sch_m2.get(suffix, f"Schedule M-2 {suffix}")

    return overrides


def write_review(rows: list[dict]) -> None:
    flagged = []
    for row in rows:
        label = row["label"]
        bad = (
            not label
            or row["confidence"] < 0.7
            or "www.irs.gov" in label.lower()
            or re.fullmatch(r"[0-9]+[a-z]?", label.lower()) is not None
        )
        if bad:
            flagged.append(row)

    lines = ["# Form 1120 Field Map Review", "", f"Flagged fields: {len(flagged)}", ""]
    for row in flagged:
        lines.append(
            f"- Page {row['page']}: `{row['field_name']}` -> `{row['label']}` (confidence {row['confidence']})"
        )
    OUTPUT_REVIEW.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    doc = fitz.open(INPUT_PDF)
    all_rows: list[dict] = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        lines = merge_multiline(line_groups(page, page_index))
        page_image = render_page_image(page) if page_index == 0 else None
        overrides: dict[str, str] = {}
        if page_index == 0:
            overrides.update(page1_overrides(page))
        elif page_index == 3:
            overrides.update(page4_overrides(page))
        elif page_index == 5:
            overrides.update(page6_overrides(page))
        page_rows: list[dict] = []
        widgets = list(page.widgets())
        for widget in widgets:
            candidates = candidates_for_widget(widget, lines, page_image)
            label = overrides.get(widget.field_name, CONFIRMED_LABELS.get(widget.field_name, candidates[0].text if candidates else ""))
            confidence = round(max(0.0, min(1.0, (candidates[0].score / 100.0))) if candidates else 0.0, 3)
            if widget.field_name in CONFIRMED_LABELS:
                confidence = 1.0
            row = {
                "page": page_index + 1,
                "field_name": widget.field_name,
                "field_type": widget.field_type_string,
                "rect": [round(value, 2) for value in widget.rect],
                "label": label,
                "confidence": confidence,
                "candidates": [
                    {
                        "text": candidate.text,
                        "mode": candidate.mode,
                        "score": round(candidate.score, 2),
                        "gap_x": round(candidate.gap_x, 2),
                        "gap_y": round(candidate.gap_y, 2),
                    }
                    for candidate in candidates[:5]
                ],
            }
            page_rows.append(row)
            all_rows.append(row)

        if page_index == 0:
            annotate_page(page, page_rows, DEBUG_DIR / "f1120-page1-annotated.png")

    with OUTPUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(all_rows, handle, indent=2)

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["page", "field_name", "field_type", "label", "confidence"],
        )
        writer.writeheader()
        for row in all_rows:
            writer.writerow({key: row[key] for key in writer.fieldnames})

    write_review(all_rows)

    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_CSV}")
    print(f"Wrote {OUTPUT_REVIEW}")
    print(f"Wrote {DEBUG_DIR / 'f1120-page1-annotated.png'}")
    print(f"Mapped {len(all_rows)} widgets across {len(doc)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
