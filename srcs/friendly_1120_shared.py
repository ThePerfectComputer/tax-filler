from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any


FRIENDLY_TOP_LEVEL_KEYS = {
    "tax_year",
    "tax_period",
    "company",
    "filing",
    "income",
    "deductions",
    "tax",
    "schedule_j",
    "schedule_k",
    "overrides",
}


@dataclass(frozen=True)
class CheckboxPair:
    yes: str
    no: str


@dataclass(frozen=True)
class Form1120Config:
    year: int
    direct_fields: dict[str, str]
    single_checkboxes: dict[str, str]
    yes_no_checkboxes: dict[str, CheckboxPair]


def looks_like_friendly_1120(values: dict[str, Any]) -> bool:
    return any(key in values for key in FRIENDLY_TOP_LEVEL_KEYS) or any(
        isinstance(value, dict) for value in values.values()
    )


def get_by_path(values: dict[str, Any], path: str) -> Any:
    current: Any = values
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def parse_decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        cleaned = stripped.replace(",", "").replace("$", "")
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None
    return None


def format_decimal(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def parse_isoish_date(value: Any) -> tuple[str, str] | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.strftime("%m/%d"), parsed.strftime("%Y")
        except ValueError:
            continue
    return None


def build_common_derived_fields(values: dict[str, Any]) -> dict[str, str]:
    derived: dict[str, str] = {}

    gross_receipts = parse_decimal(get_by_path(values, "income.gross_receipts_or_sales"))
    returns_and_allowances = parse_decimal(get_by_path(values, "income.returns_and_allowances"))
    if get_by_path(values, "income.balance") is None and gross_receipts is not None and returns_and_allowances is not None:
        derived["income.balance"] = format_decimal(gross_receipts - returns_and_allowances)

    balance = parse_decimal(get_by_path(values, "income.balance") or derived.get("income.balance"))
    cogs = parse_decimal(get_by_path(values, "income.cost_of_goods_sold"))
    if get_by_path(values, "income.gross_profit") is None and balance is not None and cogs is not None:
        derived["income.gross_profit"] = format_decimal(balance - cogs)

    income_components = [
        get_by_path(values, "income.gross_profit") or derived.get("income.gross_profit"),
        get_by_path(values, "income.dividends_and_inclusions"),
        get_by_path(values, "income.interest_income"),
        get_by_path(values, "income.gross_rents"),
        get_by_path(values, "income.gross_royalties"),
        get_by_path(values, "income.capital_gain_net_income"),
        get_by_path(values, "income.net_gain_or_loss_form_4797"),
        get_by_path(values, "income.other_income"),
    ]
    income_decimals = [parse_decimal(item) for item in income_components]
    if get_by_path(values, "income.total_income") is None and all(item is not None for item in income_decimals):
        derived["income.total_income"] = format_decimal(sum(income_decimals, Decimal("0")))

    deduction_paths = [
        "deductions.compensation_of_officers",
        "deductions.salaries_and_wages",
        "deductions.repairs_and_maintenance",
        "deductions.bad_debts",
        "deductions.rents",
        "deductions.taxes_and_licenses",
        "deductions.interest_expense",
        "deductions.charitable_contributions",
        "deductions.depreciation",
        "deductions.depletion",
        "deductions.advertising",
        "deductions.pension_profit_sharing",
        "deductions.employee_benefit_programs",
        "deductions.energy_efficient_commercial_buildings_deduction",
        "deductions.other_deductions",
    ]
    deduction_decimals = [parse_decimal(get_by_path(values, path)) for path in deduction_paths]
    if get_by_path(values, "deductions.total_deductions") is None and all(item is not None for item in deduction_decimals):
        derived["deductions.total_deductions"] = format_decimal(sum(deduction_decimals, Decimal("0")))

    total_income = parse_decimal(get_by_path(values, "income.total_income") or derived.get("income.total_income"))
    total_deductions = parse_decimal(
        get_by_path(values, "deductions.total_deductions") or derived.get("deductions.total_deductions")
    )
    if (
        get_by_path(values, "tax.taxable_income_before_nol_and_special_deductions") is None
        and total_income is not None
        and total_deductions is not None
    ):
        derived["tax.taxable_income_before_nol_and_special_deductions"] = format_decimal(total_income - total_deductions)

    nol = parse_decimal(get_by_path(values, "tax.net_operating_loss_deduction"))
    special = parse_decimal(get_by_path(values, "tax.special_deductions"))
    if get_by_path(values, "tax.total_special_deductions_and_nol") is None and nol is not None and special is not None:
        derived["tax.total_special_deductions_and_nol"] = format_decimal(nol + special)

    before_special = parse_decimal(
        get_by_path(values, "tax.taxable_income_before_nol_and_special_deductions")
        or derived.get("tax.taxable_income_before_nol_and_special_deductions")
    )
    total_special = parse_decimal(
        get_by_path(values, "tax.total_special_deductions_and_nol") or derived.get("tax.total_special_deductions_and_nol")
    )
    if get_by_path(values, "tax.taxable_income") is None and before_special is not None and total_special is not None:
        derived["tax.taxable_income"] = format_decimal(before_special - total_special)

    return derived


def resolve_with_config(
    values: dict[str, Any],
    config: Form1120Config,
    *,
    pre_resolved: dict[str, Any] | None = None,
) -> dict[str, Any]:
    derived = build_common_derived_fields(values)
    resolved: dict[str, Any] = dict(pre_resolved or {})

    begin_date = parse_isoish_date(get_by_path(values, "tax_period.begin_date"))
    if begin_date is not None:
        resolved["topmostSubform[0].Page1[0].PgHeader[0].f1_1[0]"] = begin_date[0]

    end_date = parse_isoish_date(get_by_path(values, "tax_period.end_date"))
    if end_date is not None:
        resolved["topmostSubform[0].Page1[0].PgHeader[0].f1_2[0]"] = end_date[0]
        resolved["topmostSubform[0].Page1[0].PgHeader[0].f1_3[0]"] = end_date[1]

    for path, field_name in config.direct_fields.items():
        value = get_by_path(values, path)
        if value is None:
            value = derived.get(path)
        if value is None:
            continue
        resolved[field_name] = value

    for path, field_name in config.single_checkboxes.items():
        value = get_by_path(values, path)
        if value is None:
            continue
        resolved[field_name] = value

    for path, pair in config.yes_no_checkboxes.items():
        value = get_by_path(values, path)
        if value is None:
            continue
        if value not in (True, False):
            raise SystemExit(f"Friendly checkbox field '{path}' must be true or false.")
        resolved[pair.yes] = bool(value)
        resolved[pair.no] = not bool(value)

    return resolved
