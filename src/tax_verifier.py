"""
Mathematical & Statutory Tax Verifier for US Payroll Stubs.
Strictly recalculates FICA (Social Security & Medicare), Net Pay, and YTD coherence.
"""
from typing import List, Tuple
from .models import PaystubData, RedFlag, RiskSeverity


# US Federal Statutory Tax Constants
FICA_SOCIAL_SECURITY_RATE = 0.062   # 6.2%
FICA_MEDICARE_RATE = 0.0145         # 1.45%
SOCIAL_SECURITY_WAGE_CAP_2024 = 168600.00
SOCIAL_SECURITY_WAGE_CAP_2025 = 174900.00
ROUNDING_TOLERANCE = 0.10  # 10 cents to allow for edge-case fractional rounding


class TaxVerifier:
    def __init__(self, data: PaystubData):
        self.data = data

    def verify(self) -> Tuple[List[RedFlag], List[str]]:
        red_flags: List[RedFlag] = []
        clean_signals: List[str] = []

        if self.data.gross_pay is None:
            red_flags.append(RedFlag(
                code="MISSING_GROSS_PAY",
                severity=RiskSeverity.HIGH,
                category="MATHEMATICAL",
                title="Gross Pay Amount Unidentified",
                description="Unable to parse gross income from document. Verification requires gross earnings.",
                suggested_action="Ensure paystub is clear and legible."
            ))
            return red_flags, clean_signals

        gross = self.data.gross_pay

        # ----------------------------------------------------
        # 1. FICA Social Security Recalculation (6.2%)
        # ----------------------------------------------------
        if self.data.social_security_tax is not None:
            reported_ss = self.data.social_security_tax
            expected_ss = round(gross * FICA_SOCIAL_SECURITY_RATE, 2)
            discrepancy = abs(reported_ss - expected_ss)

            if discrepancy > ROUNDING_TOLERANCE:
                pct_error = (discrepancy / expected_ss * 100) if expected_ss > 0 else 100.0
                severity = RiskSeverity.CRITICAL if discrepancy > 5.0 or pct_error > 5.0 else RiskSeverity.HIGH
                red_flags.append(RedFlag(
                    code="MATH_FICA_SS_MISMATCH",
                    severity=severity,
                    category="MATHEMATICAL",
                    title="Social Security Tax Calculation Discrepancy",
                    description=(
                        f"Reported Social Security tax is ${reported_ss:,.2f}, but statutory 6.2% "
                        f"on gross ${gross:,.2f} must be exactly ${expected_ss:,.2f} "
                        f"(Discrepancy: ${discrepancy:,.2f}, error rate: {pct_error:.1f}%). "
                        "Legitimate payroll systems compute this automatically to the penny."
                    ),
                    evidence={
                        "gross_pay": gross,
                        "reported_ss": reported_ss,
                        "expected_ss": expected_ss,
                        "discrepancy": discrepancy
                    },
                    suggested_action="High probability of manual alteration or fake generator. Cross-examine W-2."
                ))
            else:
                clean_signals.append(f"Social Security deduction strictly adheres to statutory 6.2% (${reported_ss:,.2f}).")
        else:
            red_flags.append(RedFlag(
                code="MISSING_SOCIAL_SECURITY_LINE",
                severity=RiskSeverity.MEDIUM,
                category="MATHEMATICAL",
                title="Missing FICA Social Security Line Item",
                description="Paystub lacks standard Social Security (FICA-OASDI) deduction line.",
                suggested_action="Verify if employee claims statutory exempt status."
            ))

        # ----------------------------------------------------
        # 2. FICA Medicare Recalculation (1.45%)
        # ----------------------------------------------------
        if self.data.medicare_tax is not None:
            reported_med = self.data.medicare_tax
            expected_med = round(gross * FICA_MEDICARE_RATE, 2)
            discrepancy = abs(reported_med - expected_med)

            if discrepancy > ROUNDING_TOLERANCE:
                pct_error = (discrepancy / expected_med * 100) if expected_med > 0 else 100.0
                severity = RiskSeverity.CRITICAL if discrepancy > 3.0 or pct_error > 5.0 else RiskSeverity.HIGH
                red_flags.append(RedFlag(
                    code="MATH_FICA_MEDICARE_MISMATCH",
                    severity=severity,
                    category="MATHEMATICAL",
                    title="Medicare Tax Calculation Discrepancy",
                    description=(
                        f"Reported Medicare tax is ${reported_med:,.2f}, but statutory 1.45% "
                        f"on gross ${gross:,.2f} must be ${expected_med:,.2f} "
                        f"(Discrepancy: ${discrepancy:,.2f})."
                    ),
                    evidence={
                        "gross_pay": gross,
                        "reported_med": reported_med,
                        "expected_med": expected_med,
                        "discrepancy": discrepancy
                    },
                    suggested_action="Flag for landlord scrutiny. Commercial payroll engines never miscalculate Medicare."
                ))
            else:
                clean_signals.append(f"Medicare deduction matches statutory 1.45% (${reported_med:,.2f}).")

        # ----------------------------------------------------
        # 3. Net Pay Reconciliation (Gross - Deductions == Net)
        # ----------------------------------------------------
        if self.data.net_pay is not None and self.data.total_deductions is not None:
            net = self.data.net_pay
            deductions = self.data.total_deductions
            expected_net = round(gross - deductions, 2)
            discrepancy = abs(net - expected_net)

            if discrepancy > ROUNDING_TOLERANCE:
                red_flags.append(RedFlag(
                    code="MATH_NET_PAY_FORMULA_BROKEN",
                    severity=RiskSeverity.CRITICAL,
                    category="MATHEMATICAL",
                    title="Net Pay Arithmetic Inconsistency",
                    description=(
                        f"Reported Net Pay is ${net:,.2f}, but Gross (${gross:,.2f}) minus "
                        f"Total Deductions (${deductions:,.2f}) equals ${expected_net:,.2f} "
                        f"(Discrepancy: ${discrepancy:,.2f}). "
                        "The arithmetic does not balance."
                    ),
                    evidence={
                        "gross_pay": gross,
                        "total_deductions": deductions,
                        "reported_net": net,
                        "calculated_net": expected_net,
                        "discrepancy": discrepancy
                    },
                    suggested_action="Reject document immediately. Fundamental math failure indicates manual forgery."
                ))
            else:
                clean_signals.append("Gross Pay, Total Deductions, and Net Pay reconcile seamlessly.")

        # ----------------------------------------------------
        # 4. Deductions Breakdown Sum Check
        # Only evaluate when federal income tax is explicitly tracked
        # ----------------------------------------------------
        if self.data.total_deductions is not None and self.data.federal_income_tax is not None:
            deduction_items = [
                self.data.social_security_tax,
                self.data.medicare_tax,
                self.data.federal_income_tax,
                self.data.state_income_tax,
                self.data.other_deductions
            ]
            valid_items = [item for item in deduction_items if item is not None]
            sum_items = round(sum(valid_items), 2)
            diff = abs(sum_items - self.data.total_deductions)
            if diff > ROUNDING_TOLERANCE:
                if diff > 10.0:
                    red_flags.append(RedFlag(
                        code="MATH_DEDUCTION_SUM_DISCREPANCY",
                        severity=RiskSeverity.MEDIUM,
                        category="MATHEMATICAL",
                        title="Deductions Sum Discrepancy",
                        description=(
                            f"Sum of visible deduction lines (${sum_items:,.2f}) does not match "
                            f"Total Deductions line (${self.data.total_deductions:,.2f})."
                        ),
                        evidence={"sum_items": sum_items, "reported_total": self.data.total_deductions},
                        suggested_action="Review if pre-tax benefits (401k/Health) account for the difference."
                    ))

        # ----------------------------------------------------
        # 5. Year-To-Date (YTD) Coherence
        # ----------------------------------------------------
        if self.data.ytd_gross is not None:
            if self.data.ytd_gross < gross:
                red_flags.append(RedFlag(
                    code="MATH_YTD_LESS_THAN_CURRENT",
                    severity=RiskSeverity.CRITICAL,
                    category="MATHEMATICAL",
                    title="Imposible YTD Gross Earnings",
                    description=(
                        f"Cumulative YTD Gross (${self.data.ytd_gross:,.2f}) is strictly less than "
                        f"current period Gross Pay (${gross:,.2f})."
                    ),
                    evidence={"current_gross": gross, "ytd_gross": self.data.ytd_gross},
                    suggested_action="High-confidence counterfeit. Reject application."
                ))
            else:
                clean_signals.append(f"YTD Gross (${self.data.ytd_gross:,.2f}) logically exceeds period gross.")

        return red_flags, clean_signals
