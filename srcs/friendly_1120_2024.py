from __future__ import annotations

from typing import Any

from friendly_1120_shared import CheckboxPair, Form1120Config, get_by_path, resolve_with_config


PAGE1 = "topmostSubform[0].Page1[0]"
TYPE = f"{PAGE1}.TypeOrPrintBox[0]"
A = f"{PAGE1}.A[0]"


def _build_config() -> Form1120Config:
    direct_fields = {
        "company.name": f"{TYPE}.f1_4[0]",
        "company.ein": f"{PAGE1}.f1_7[0]",
        "company.date_incorporated": f"{PAGE1}.f1_8[0]",
        "company.total_assets": f"{PAGE1}.f1_9[0]",
        "company.business_activity_code": "topmostSubform[0].Page4[0].f4_2[0]",
        "company.business_activity": "topmostSubform[0].Page4[0].f4_3[0]",
        "company.product_or_service": "topmostSubform[0].Page4[0].f4_4[0]",
    }

    ordered_amount_paths = [
        "income.gross_receipts_or_sales",
        "income.returns_and_allowances",
        "income.balance",
        "income.cost_of_goods_sold",
        "income.gross_profit",
        "income.dividends_and_inclusions",
        "income.interest_income",
        "income.gross_rents",
        "income.gross_royalties",
        "income.capital_gain_net_income",
        "income.net_gain_or_loss_form_4797",
        "income.other_income",
        "income.total_income",
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
        "deductions.total_deductions",
        "tax.taxable_income_before_nol_and_special_deductions",
        "tax.net_operating_loss_deduction",
        "tax.special_deductions",
        "tax.total_special_deductions_and_nol",
        "tax.taxable_income",
    ]
    for offset, path in enumerate(ordered_amount_paths, start=10):
        direct_fields[path] = f"{PAGE1}.f1_{offset}[0]"

    direct_fields.update(
        {
            "tax.total_tax": f"{PAGE1}.f1_44[0]",
            "tax.total_payments_and_credits": f"{PAGE1}.f1_46[0]",
            "tax.estimated_tax_penalty": f"{PAGE1}.f1_47[0]",
            "tax.amount_owed": f"{PAGE1}.f1_48[0]",
            "tax.overpayment": f"{PAGE1}.f1_49[0]",
            "tax.credit_to_next_year": f"{PAGE1}.f1_50[0]",
            "tax.refunded_amount": f"{PAGE1}.f1_51[0]",
            "schedule_j.income_tax": "topmostSubform[0].Page3[0].f3_1[0]",
            "schedule_j.tax_from_form_1120_l": "topmostSubform[0].Page3[0].f3_2[0]",
            "schedule_j.section_1291_tax": "topmostSubform[0].Page3[0].f3_3[0]",
            "schedule_j.tax_adjustment_form_8978": "topmostSubform[0].Page3[0].f3_4[0]",
            "schedule_j.additional_tax_under_197f": "topmostSubform[0].Page3[0].f3_5[0]",
            "schedule_j.base_erosion_minimum_tax": "topmostSubform[0].Page3[0].f3_6[0]",
            "schedule_j.amount_from_form_4255_q": "topmostSubform[0].Page3[0].f3_7[0]",
            "schedule_j.other_chapter_1_tax": "topmostSubform[0].Page3[0].f3_8[0]",
            "schedule_j.total_income_tax": "topmostSubform[0].Page3[0].f3_9[0]",
            "schedule_j.corporate_alternative_minimum_tax": "topmostSubform[0].Page3[0].f3_10[0]",
            "schedule_j.add_lines_2_and_3": "topmostSubform[0].Page3[0].f3_11[0]",
            "schedule_j.foreign_tax_credit": "topmostSubform[0].Page3[0].f3_12[0]",
            "schedule_j.credit_from_form_8834": "topmostSubform[0].Page3[0].f3_13[0]",
            "schedule_j.general_business_credit": "topmostSubform[0].Page3[0].f3_14[0]",
            "schedule_j.credit_for_prior_year_minimum_tax": "topmostSubform[0].Page3[0].f3_15[0]",
            "schedule_j.bond_credits": "topmostSubform[0].Page3[0].f3_16[0]",
            "schedule_j.adjustment_from_form_8978": "topmostSubform[0].Page3[0].f3_17[0]",
            "schedule_j.total_credits": "topmostSubform[0].Page3[0].f3_18[0]",
            "schedule_j.tax_after_credits": "topmostSubform[0].Page3[0].f3_19[0]",
            "schedule_j.personal_holding_company_tax": "topmostSubform[0].Page3[0].f3_20[0]",
            "schedule_j.amount_from_form_4255_r": "topmostSubform[0].Page3[0].f3_21[0]",
            "schedule_j.recapture_low_income_housing_credit": "topmostSubform[0].Page3[0].f3_22[0]",
            "schedule_j.long_term_contract_lookback_interest": "topmostSubform[0].Page3[0].f3_23[0]",
            "schedule_j.income_forecast_lookback_interest": "topmostSubform[0].Page3[0].f3_24[0]",
            "schedule_j.alternative_tax_on_qualifying_shipping": "topmostSubform[0].Page3[0].f3_25[0]",
            "schedule_j.interest_tax_due_section_453a": "topmostSubform[0].Page3[0].f3_26[0]",
            "schedule_j.interest_tax_due_section_453l": "topmostSubform[0].Page3[0].f3_27[0]",
            "schedule_j.other_taxes": "topmostSubform[0].Page3[0].f3_28[0]",
            "schedule_j.total_other_taxes": "topmostSubform[0].Page3[0].f3_29[0]",
            "schedule_j.total_tax_before_deferred_taxes": "topmostSubform[0].Page3[0].f3_30[0]",
            "schedule_j.deferred_tax_qef": "topmostSubform[0].Page3[0].f3_31[0]",
            "schedule_j.deferred_lifo_recapture_tax": "topmostSubform[0].Page3[0].f3_32[0]",
            "schedule_j.total_tax_after_deferred_taxes": "topmostSubform[0].Page3[0].f3_33[0]",
            "schedule_j.preceding_year_overpayment_credit": "topmostSubform[0].Page3[0].f3_34[0]",
            "schedule_j.current_year_estimated_tax_payments": "topmostSubform[0].Page3[0].f3_35[0]",
            "schedule_j.refund_applied_on_form_4466": "topmostSubform[0].Page3[0].f3_36[0]",
            "schedule_j.tax_deposited_with_form_7004": "topmostSubform[0].Page3[0].f3_38[0]",
            "schedule_j.withholding": "topmostSubform[0].Page3[0].f3_39[0]",
            "schedule_j.total_payments": "topmostSubform[0].Page3[0].f3_40[0]",
            "schedule_j.refundable_credit_form_2439": "topmostSubform[0].Page3[0].f3_41[0]",
            "schedule_j.refundable_credit_form_4136": "topmostSubform[0].Page3[0].f3_42[0]",
            "schedule_j.refundable_credit_withheld_forms": "topmostSubform[0].Page3[0].f3_43[0]",
            "schedule_j.refundable_credit_other": "topmostSubform[0].Page3[0].f3_44[0]",
            "schedule_j.total_refundable_credits": "topmostSubform[0].Page3[0].f3_45[0]",
            "schedule_j.elective_payment_election_amount": "topmostSubform[0].Page3[0].f3_46[0]",
            "schedule_j.total_payments_credits_and_section_1062": "topmostSubform[0].Page3[0].f3_47[0]",
            "schedule_k.cash_and_property_distributions_amount": "topmostSubform[0].Page5[0].f5_1[0]",
            "schedule_k.disallowed_267a_deductions_amount": "topmostSubform[0].Page5[0].f5_2[0]",
            "schedule_k.qualified_opportunity_fund_amount": "topmostSubform[0].Page5[0].f5_3[0]",
            "schedule_k.section_7874_percentage_by_vote": "topmostSubform[0].Page5[0].f5_4[0]",
            "schedule_k.section_7874_percentage_by_value": "topmostSubform[0].Page5[0].f5_5[0]",
        }
    )

    single_checkboxes = {
        "filing.consolidated_return": f"{A}.c1_1[0]",
        "filing.life_nonlife_consolidated_return": f"{A}.c1_2[0]",
        "filing.personal_holding_company": f"{A}.c1_3[0]",
        "filing.personal_service_corporation": f"{A}.c1_4[0]",
        "filing.schedule_m3_attached": f"{A}.c1_5[0]",
        "filing.initial_return": f"{PAGE1}.c1_6[0]",
        "filing.final_return": f"{PAGE1}.c1_7[0]",
        "filing.name_change": f"{PAGE1}.c1_8[0]",
        "filing.address_change": f"{PAGE1}.c1_9[0]",
    }

    yes_no = {
        "schedule_k.small_corp_exception": CheckboxPair("topmostSubform[0].Page5[0].c5_1[0]", "topmostSubform[0].Page5[0].c5_1[1]"),
        "schedule_k.schedule_utp_required": CheckboxPair("topmostSubform[0].Page5[0].c5_2[0]", "topmostSubform[0].Page5[0].c5_2[1]"),
        "schedule_k.payments_require_1099": CheckboxPair("topmostSubform[0].Page5[0].c5_3[0]", "topmostSubform[0].Page5[0].c5_3[1]"),
        "schedule_k.files_required_1099": CheckboxPair("topmostSubform[0].Page5[0].c5_4[0]", "topmostSubform[0].Page5[0].c5_4[1]"),
        "schedule_k.ownership_change_80_percent": CheckboxPair("topmostSubform[0].Page5[0].c5_5[0]", "topmostSubform[0].Page5[0].c5_5[1]"),
        "schedule_k.disposed_more_than_65_percent_assets": CheckboxPair("topmostSubform[0].Page5[0].c5_6[0]", "topmostSubform[0].Page5[0].c5_6[1]"),
        "schedule_k.received_section_351_assets_over_1m": CheckboxPair("topmostSubform[0].Page5[0].c5_7[0]", "topmostSubform[0].Page5[0].c5_7[1]"),
        "schedule_k.payments_require_1042_1042s": CheckboxPair("topmostSubform[0].Page5[0].c5_8[0]", "topmostSubform[0].Page5[0].c5_8[1]"),
        "schedule_k.operating_on_cooperative_basis": CheckboxPair("topmostSubform[0].Page5[0].c5_9[0]", "topmostSubform[0].Page5[0].c5_9[1]"),
        "schedule_k.deduction_disallowed_under_267a": CheckboxPair("topmostSubform[0].Page5[0].c5_10[0]", "topmostSubform[0].Page5[0].c5_10[1]"),
        "schedule_k.gross_receipts_at_least_500m": CheckboxPair("topmostSubform[0].Page5[0].c5_11[0]", "topmostSubform[0].Page5[0].c5_11[1]"),
        "schedule_k.section_163j_real_property_or_farming_election": CheckboxPair("topmostSubform[0].Page5[0].c5_12[0]", "topmostSubform[0].Page5[0].c5_12[1]"),
        "schedule_k.form_8990_required": CheckboxPair("topmostSubform[0].Page5[0].c5_13[0]", "topmostSubform[0].Page5[0].c5_13[1]"),
        "schedule_k.qualified_opportunity_fund": CheckboxPair("topmostSubform[0].Page5[0].c5_14[0]", "topmostSubform[0].Page5[0].c5_14[1]"),
        "schedule_k.section_7874_inversion": CheckboxPair("topmostSubform[0].Page5[0].c5_15[0]", "topmostSubform[0].Page5[0].c5_15[1]"),
        "schedule_k.digital_asset_activity": CheckboxPair("topmostSubform[0].Page5[0].c5_16[0]", "topmostSubform[0].Page5[0].c5_16[1]"),
        "schedule_k.controlled_group_member": CheckboxPair("topmostSubform[0].Page5[0].c5_17[0]", "topmostSubform[0].Page5[0].c5_17[1]"),
        "schedule_k.corporate_amt_prior_year_applicable_corporation": CheckboxPair("topmostSubform[0].Page5[0].c5_18[0]", "topmostSubform[0].Page5[0].c5_18[1]"),
        "schedule_k.corporate_amt_current_year_due_to_prior_year": CheckboxPair("topmostSubform[0].Page5[0].c5_19[0]", "topmostSubform[0].Page5[0].c5_19[1]"),
        "schedule_k.corporate_amt_safe_harbor": CheckboxPair("topmostSubform[0].Page5[0].c5_20[0]", "topmostSubform[0].Page5[0].c5_20[1]"),
        "schedule_k.form_7208_under_covered_corporation_rules": CheckboxPair("topmostSubform[0].Page5[0].c5_21[0]", "topmostSubform[0].Page5[0].c5_21[1]"),
        "schedule_k.form_7208_under_applicable_foreign_corporation_rules": CheckboxPair("topmostSubform[0].Page5[0].c5_22[0]", "topmostSubform[0].Page5[0].c5_22[1]"),
        "schedule_k.form_7208_under_covered_surrogate_foreign_corporation_rules": CheckboxPair("topmostSubform[0].Page5[0].c5_23[0]", "topmostSubform[0].Page5[0].c5_23[1]"),
        "schedule_k.large_subchapter_k_basis_adjustment": CheckboxPair("topmostSubform[0].Page5[0].c5_24[0]", "topmostSubform[0].Page5[0].c5_24[1]"),
        "schedule_k.foreign_owner_25_percent": CheckboxPair("topmostSubform[0].Page4[0].c4_8[0]", "topmostSubform[0].Page4[0].c4_8[1]"),
    }

    return Form1120Config(year=2024, direct_fields=direct_fields, single_checkboxes=single_checkboxes, yes_no_checkboxes=yes_no)


CONFIG_2024 = _build_config()


def resolve_friendly_1120_2024_values(values: dict[str, Any]) -> dict[str, Any]:
    pre_resolved: dict[str, Any] = {}
    street = get_by_path(values, "company.address.street")
    suite = get_by_path(values, "company.address.suite")
    line1 = " ".join(str(part).strip() for part in [street, suite] if part not in (None, ""))
    if line1:
        pre_resolved[f"{TYPE}.f1_5[0]"] = line1

    city = get_by_path(values, "company.address.city")
    state = get_by_path(values, "company.address.state")
    country = get_by_path(values, "company.address.country")
    postal_code = get_by_path(values, "company.address.postal_code")
    location_parts = [str(part).strip() for part in [city, state, country] if part not in (None, "")]
    location_line = ", ".join(location_parts)
    if postal_code not in (None, ""):
        postal_text = str(postal_code).strip()
        location_line = f"{location_line} {postal_text}".strip() if location_line else postal_text
    if location_line:
        pre_resolved[f"{TYPE}.f1_6[0]"] = location_line

    return resolve_with_config(values, CONFIG_2024, pre_resolved=pre_resolved)
