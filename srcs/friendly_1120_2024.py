from __future__ import annotations

from typing import Any

from friendly_1120_shared import CheckboxPair, ChoiceCheckboxGroup, Form1120Config, get_by_path, resolve_with_config


PAGE1 = "topmostSubform[0].Page1[0]"
TYPE = f"{PAGE1}.TypeOrPrintBox[0]"
A = f"{PAGE1}.A[0]"
PAGE2 = "topmostSubform[0].Page2[0].Pg2Table[0]"
PAGE4 = "topmostSubform[0].Page4[0]"
PAGE5 = "topmostSubform[0].Page5[0]"
PAGE6 = "topmostSubform[0].Page6[0]"


def _add_schedule_c_fields(direct_fields: dict[str, str]) -> None:
    row_specs = [
        ("line_1", "Line1", 1),
        ("line_2", "Line2", 4),
        ("line_3", "Line3", 7),
        ("line_4", "Line4", 10),
        ("line_5", "Line5", 13),
        ("line_6", "Line6", 16),
        ("line_7", "Line7", 19),
        ("line_8", "Line8", 22),
        ("line_9", "Line9", 25),
        ("line_10", "Line10", 28),
        ("line_11", "Line11", 31),
        ("line_12", "Line12", 34),
        ("line_13", "Line13", 37),
        ("line_14", "Line14", 40),
        ("line_15", "Line15", 43),
        ("line_16a", "Line16a", 46),
        ("line_16b", "Line16b", 49),
        ("line_16c", "Line16c", 52),
        ("line_17", "Line17", 55),
        ("line_18", "Line18", 58),
        ("line_19", "Line19", 61),
        ("line_20", "Line20", 64),
        ("line_21", "Line21", 67),
        ("line_22", "Line22", 70),
        ("line_23", "Line23", 73),
    ]
    for slug, row_name, start in row_specs:
        direct_fields[f"schedule_c.{slug}.dividends_and_inclusions"] = f"{PAGE2}.{row_name}[0].f2_{start}[0]"
        direct_fields[f"schedule_c.{slug}.percentage"] = f"{PAGE2}.{row_name}[0].f2_{start + 1}[0]"
        direct_fields[f"schedule_c.{slug}.special_deductions"] = f"{PAGE2}.{row_name}[0].f2_{start + 2}[0]"
    direct_fields["schedule_c.total_special_deductions"] = "topmostSubform[0].Page2[0].f2_76[0]"


def _add_schedule_k_page4_fields(
    direct_fields: dict[str, str],
    single_checkboxes: dict[str, str],
    yes_no: dict[str, CheckboxPair],
    choice_checkboxes: dict[str, ChoiceCheckboxGroup],
) -> None:
    choice_checkboxes["schedule_k.accounting_method"] = ChoiceCheckboxGroup(
        options={
            "cash": (f"{PAGE4}.c4_1[0]",),
            "accrual": (f"{PAGE4}.c4_1[1]",),
            "other": (f"{PAGE4}.c4_1[2]",),
        }
    )
    direct_fields["schedule_k.other_accounting_method"] = f"{PAGE4}.f4_1[0]"
    yes_no.update(
        {
            "schedule_k.subsidiary_in_affiliated_group": CheckboxPair(f"{PAGE4}.c4_2[0]", f"{PAGE4}.c4_2[1]"),
            "schedule_k.entity_owned_stock_20_or_50_percent": CheckboxPair(f"{PAGE4}.c4_3[0]", f"{PAGE4}.c4_3[1]"),
            "schedule_k.individual_owned_stock_20_or_50_percent": CheckboxPair(f"{PAGE4}.c4_4[0]", f"{PAGE4}.c4_4[1]"),
            "schedule_k.owns_other_corporation_stock": CheckboxPair(f"{PAGE4}.c4_5[0]", f"{PAGE4}.c4_5[1]"),
            "schedule_k.owns_partnership_or_trust_interest": CheckboxPair(f"{PAGE4}.c4_6[0]", f"{PAGE4}.c4_6[1]"),
            "schedule_k.paid_dividends_in_excess_of_earnings": CheckboxPair(f"{PAGE4}.c4_7[0]", f"{PAGE4}.c4_7[1]"),
        }
    )
    direct_fields["schedule_k.parent_corporation_name_and_ein"] = f"{PAGE4}.f4_5[0]"
    direct_fields["schedule_k.line_5a_table.row_1.extra_field"] = f"{PAGE4}.f4_6[0]"

    for row_index, field_numbers in enumerate(((7, 8, 9, 10), (11, 12, 13, 14), (15, 16, 17, 18)), start=1):
        prefix = f"schedule_k.line_5a_table.row_{row_index}"
        row = f"{PAGE4}.Line5aTable[0].BodyRow{row_index}[0]"
        for column_index, field_number in enumerate(field_numbers, start=1):
            direct_fields[f"{prefix}.field_{column_index}"] = f"{row}.f4_{field_number}[0]"

    for row_index, field_numbers in enumerate(((18, 19, 20, 21, 22), (23, 24, 25, 26), (27, 28, 29, 30)), start=1):
        prefix = f"schedule_k.line_5b_table.row_{row_index}"
        row = f"{PAGE4}.Line5bTable[0].BodyRow{row_index}[0]"
        for column_index, field_number in enumerate(field_numbers, start=1):
            direct_fields[f"{prefix}.field_{column_index}"] = f"{row}.f4_{field_number}[0]"
    direct_fields["schedule_k.foreign_owner_percentage"] = f"{PAGE4}.f4_31[0]"
    direct_fields["schedule_k.foreign_owner_country"] = f"{PAGE4}.f4_32[0]"
    direct_fields["schedule_k.forms_5472_attached_count"] = f"{PAGE4}.f4_33[0]"
    single_checkboxes["schedule_k.publicly_offered_debt_with_oid"] = f"{PAGE4}.c4_9[0]"
    direct_fields["schedule_k.tax_exempt_interest_received_or_accrued"] = f"{PAGE4}.f4_34[0]"
    direct_fields["schedule_k.shareholder_count"] = f"{PAGE4}.f4_35[0]"
    single_checkboxes["schedule_k.elect_to_forego_nol_carryback"] = f"{PAGE4}.c4_10[0]"
    direct_fields["schedule_k.available_nol_carryover"] = f"{PAGE4}.f4_36[0]"


def _add_schedule_l_m1_m2_fields(direct_fields: dict[str, str]) -> None:
    asset_rows = [
        ("cash", "Line1", 1),
        ("trade_notes_and_accounts_receivable", "Line2a", 5),
        ("less_allowance_for_bad_debts", "Line2b", 9),
        ("inventories", "Line3", 13),
        ("us_government_obligations", "Line4", 17),
        ("tax_exempt_securities", "Line5", 21),
        ("other_current_assets", "Line6", 25),
        ("loans_to_shareholders", "Line7", 29),
        ("mortgage_and_real_estate_loans", "Line8", 33),
        ("other_investments", "Line9", 37),
        ("buildings_and_other_depreciable_assets", "Line10a", 41),
        ("less_accumulated_depreciation", "Line10b", 45),
        ("depletable_assets", "Line11a", 49),
        ("less_accumulated_depletion", "Line11b", 53),
        ("land", "Line12", 57),
        ("intangible_assets_amortizable_only", "Line13a", 61),
        ("less_accumulated_amortization", "Line13b", 65),
        ("other_assets", "Line14", 69),
        ("total_assets", "Line15", 73),
    ]
    liability_rows = [
        ("accounts_payable", "Line16", 77),
        ("mortgages_notes_bonds_payable_less_than_one_year", "Line17", 81),
        ("other_current_liabilities", "Line18", 85),
        ("loans_from_shareholders", "Line19", 89),
        ("mortgages_notes_bonds_payable_one_year_or_more", "Line20", 93),
        ("other_liabilities", "Line21", 97),
        ("capital_stock_preferred", "Line22a", 101),
        ("capital_stock_common", "Line22b", 105),
        ("additional_paid_in_capital", "Line23", 109),
        ("retained_earnings_appropriated", "Line24", 113),
        ("retained_earnings_unappropriated", "Line25", 117),
        ("adjustments_to_shareholders_equity", "Line26", 121),
        ("less_cost_of_treasury_stock", "Line27", 125),
        ("total_liabilities_and_shareholders_equity", "Line28", 129),
    ]
    columns = [("beginning_a", 0), ("beginning_b", 1), ("end_c", 2), ("end_d", 3)]

    for slug, row_name, base in asset_rows:
        for column_name, offset in columns:
            direct_fields[f"schedule_l.assets.{slug}.{column_name}"] = f"{PAGE6}.SchLTable[0].{row_name}[0].f6_{base + offset}[0]"

    for slug, row_name, base in liability_rows:
        for column_name, offset in columns:
            direct_fields[f"schedule_l.liabilities_and_equity.{slug}.{column_name}"] = (
                f"{PAGE6}.SchLTable[0].{row_name}[0].f6_{base + offset}[0]"
            )

    direct_fields.update(
        {
            "schedule_m1.net_income_loss_per_books": f"{PAGE6}.SchM-1_Left[0].f6_133[0]",
            "schedule_m1.federal_income_tax_per_books": f"{PAGE6}.SchM-1_Left[0].f6_134[0]",
            "schedule_m1.excess_capital_losses_over_capital_gains": f"{PAGE6}.SchM-1_Left[0].f6_135[0]",
            "schedule_m1.income_subject_to_tax_not_recorded_description": f"{PAGE6}.SchM-1_Left[0].f6_136[0]",
            "schedule_m1.income_subject_to_tax_not_recorded_amount": f"{PAGE6}.SchM-1_Left[0].f6_137[0]",
            "schedule_m1.expenses_not_deducted_description": f"{PAGE6}.SchM-1_Left[0].f6_138[0]",
            "schedule_m1.expenses_not_deducted_depreciation": f"{PAGE6}.SchM-1_Left[0].f6_139[0]",
            "schedule_m1.expenses_not_deducted_charitable_contributions": f"{PAGE6}.SchM-1_Left[0].f6_140[0]",
            "schedule_m1.expenses_not_deducted_travel_and_entertainment": f"{PAGE6}.SchM-1_Left[0].f6_141[0]",
            "schedule_m1.expenses_not_deducted_other": f"{PAGE6}.SchM-1_Left[0].f6_142[0]",
            "schedule_m1.add_lines_7_and_8_left_copy": f"{PAGE6}.SchM-1_Left[0].f6_143[0]",
            "schedule_m1.add_lines_1_through_5": f"{PAGE6}.SchM-1_Left[0].f6_144[0]",
            "schedule_m1.tax_exempt_interest_amount": f"{PAGE6}.SchM-1_Right[0].f6_145[0]",
            "schedule_m1.tax_exempt_interest_description": f"{PAGE6}.SchM-1_Right[0].f6_146[0]",
            "schedule_m1.deductions_not_charged_description": f"{PAGE6}.SchM-1_Right[0].f6_147[0]",
            "schedule_m1.deductions_not_charged_amount": f"{PAGE6}.SchM-1_Right[0].f6_148[0]",
            "schedule_m1.deductions_not_charged_depreciation": f"{PAGE6}.SchM-1_Right[0].f6_149[0]",
            "schedule_m1.deductions_not_charged_charitable_contributions": f"{PAGE6}.SchM-1_Right[0].f6_150[0]",
            "schedule_m1.deductions_not_charged_travel_and_entertainment": f"{PAGE6}.SchM-1_Right[0].f6_151[0]",
            "schedule_m1.deductions_not_charged_other": f"{PAGE6}.SchM-1_Right[0].f6_152[0]",
            "schedule_m1.add_lines_7_and_8": f"{PAGE6}.SchM-1_Right[0].f6_153[0]",
            "schedule_m1.line_10_line_6_less_line_9": f"{PAGE6}.SchM-1_Right[0].f6_154[0]",
            "schedule_m1.line_10_income_page_1_line_28": f"{PAGE6}.SchM-1_Right[0].f6_155[0]",
            "schedule_m2.balance_at_beginning_of_year": f"{PAGE6}.SchM-2_Left[0].f6_156[0]",
            "schedule_m2.net_income_loss_per_books": f"{PAGE6}.SchM-2_Left[0].f6_157[0]",
            "schedule_m2.other_increases_description": f"{PAGE6}.SchM-2_Left[0].f6_158[0]",
            "schedule_m2.other_increases_amount": f"{PAGE6}.SchM-2_Left[0].f6_159[0]",
            "schedule_m2.add_lines_1_2_and_3": f"{PAGE6}.SchM-2_Left[0].f6_160[0]",
            "schedule_m2.other_decreases_description_left_copy": f"{PAGE6}.SchM-2_Left[0].f6_161[0]",
            "schedule_m2.add_lines_1_2_and_3_amount": f"{PAGE6}.SchM-2_Left[0].f6_162[0]",
            "schedule_m2.other_decreases_description": f"{PAGE6}.SchM-2_Right[0].f6_166[0]",
            "schedule_m2.other_decreases_amount": f"{PAGE6}.SchM-2_Right[0].f6_167[0]",
            "schedule_m2.distributions_cash": f"{PAGE6}.SchM-2_Right[0].f6_163[0]",
            "schedule_m2.distributions_stock": f"{PAGE6}.SchM-2_Right[0].f6_164[0]",
            "schedule_m2.distributions_property": f"{PAGE6}.SchM-2_Right[0].f6_165[0]",
            "schedule_m2.add_lines_5_and_6": f"{PAGE6}.SchM-2_Right[0].f6_168[0]",
            "schedule_m2.balance_at_end_of_year": f"{PAGE6}.SchM-2_Right[0].f6_169[0]",
        }
    )


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

    direct_fields["tax.taxable_income"] = f"{PAGE1}.f1_43[0]"

    direct_fields.update(
        {
            "tax.total_tax": f"{PAGE1}.f1_44[0]",
            "tax.reserved_for_future_use": f"{PAGE1}.f1_45[0]",
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
            "schedule_j.reserved_for_future_use": "topmostSubform[0].Page3[0].f3_37[0]",
        }
    )

    _add_schedule_c_fields(direct_fields)

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
        "tax.form_2220_attached": f"{PAGE1}.c1_10[0]",
        "signing.irs_may_discuss_with_preparer": f"{PAGE1}.c1_12[0]",
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

    choice_checkboxes: dict[str, ChoiceCheckboxGroup] = {
        "schedule_k.accounting_method": ChoiceCheckboxGroup(
            options={
                "cash": (f"{PAGE4}.c4_1[0]",),
                "accrual": (f"{PAGE4}.c4_1[1]",),
                "other": (f"{PAGE4}.c4_1[2]",),
            }
        ),
        "tax.refund_deposit_account_type": ChoiceCheckboxGroup(
            options={
                "checking": (f"{PAGE1}.c1_11[0]",),
                "savings": (f"{PAGE1}.c1_11[1]",),
            }
        ),
    }
    direct_fields.update(
        {
            "deductions.rents": f"{PAGE1}.f1_27[0]",
            "deductions.taxes_and_licenses": f"{PAGE1}.f1_28[0]",
            "deductions.interest_expense": f"{PAGE1}.f1_29[0]",
            "deductions.charitable_contributions": f"{PAGE1}.f1_30[0]",
            "deductions.depreciation": f"{PAGE1}.f1_31[0]",
            "deductions.depletion": f"{PAGE1}.f1_32[0]",
            "deductions.advertising": f"{PAGE1}.f1_33[0]",
            "deductions.pension_profit_sharing": f"{PAGE1}.f1_34[0]",
            "deductions.employee_benefit_programs": f"{PAGE1}.f1_35[0]",
            "deductions.energy_efficient_commercial_buildings_deduction": f"{PAGE1}.f1_36[0]",
            "deductions.other_deductions": f"{PAGE1}.f1_37[0]",
            "deductions.total_deductions": f"{PAGE1}.f1_38[0]",
            "tax.taxable_income_before_nol_and_special_deductions": f"{PAGE1}.f1_39[0]",
            "tax.net_operating_loss_deduction": f"{PAGE1}.f1_40[0]",
            "tax.special_deductions": f"{PAGE1}.f1_41[0]",
            "tax.total_special_deductions_and_nol": f"{PAGE1}.f1_42[0]",
            "tax.routing_number": f"{PAGE1}.f1_52[0]",
            "signing.officer_signature": f"{PAGE1}.f1_53[0]",
            "signing.date": f"{PAGE1}.f1_54[0]",
            "signing.title": f"{PAGE1}.f1_55[0]",
            "paid_preparer.signature": f"{PAGE1}.f1_56[0]",
            "paid_preparer.date_or_ptin": f"{PAGE1}.f1_57[0]",
            "paid_preparer.additional_field": f"{PAGE1}.f1_58[0]",
        }
    )
    _add_schedule_k_page4_fields(direct_fields, single_checkboxes, yes_no, choice_checkboxes)
    _add_schedule_l_m1_m2_fields(direct_fields)

    return Form1120Config(
        year=2024,
        direct_fields=direct_fields,
        single_checkboxes=single_checkboxes,
        yes_no_checkboxes=yes_no,
        choice_checkboxes=choice_checkboxes,
    )


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
