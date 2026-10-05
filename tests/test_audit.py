"""
Automated Accuracy Test Suite for TenantGuard AI Core Engine.
Evaluates 10 distinct scenario profiles (Legitimate vs. Counterfeit).
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import TenantGuardAnalyzer, PaystubData, RiskSeverity


class TestTenantGuardAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TenantGuardAnalyzer()

    # --- LEGITIMATE PROFILES (Expected: LOW RISK, Score <= 10) ---

    def test_01_legit_standard_biweekly(self):
        """Alice: Clean salaried worker, ADP payroll, exact 6.2% SS and 1.45% Med."""
        data = PaystubData(
            gross_pay=3500.00,
            social_security_tax=217.00,  # 3500 * 0.062 = 217.00
            medicare_tax=50.75,          # 3500 * 0.0145 = 50.75
            federal_income_tax=380.00,
            state_income_tax=120.00,
            total_deductions=767.75,     # 217 + 50.75 + 380 + 120 = 767.75
            net_pay=2732.25,             # 3500 - 767.75 = 2732.25
            ytd_gross=28000.00
        )
        res = self.analyzer.analyze_structured_data(data)
        self.assertEqual(res.risk_level, "LOW RISK")
        self.assertEqual(res.risk_score, 0)
        self.assertEqual(len(res.red_flags), 0)

    def test_02_legit_hourly_with_cents(self):
        """Bob: Hourly worker with odd cents ($2,143.50)."""
        data = PaystubData(
            gross_pay=2143.50,
            social_security_tax=132.90,  # 2143.50 * 0.062 = 132.897 -> 132.90
            medicare_tax=31.08,          # 2143.50 * 0.0145 = 31.0807 -> 31.08
            federal_income_tax=210.00,
            state_income_tax=76.02,
            total_deductions=450.00,     # 132.90 + 31.08 + 210.00 + 76.02 = 450.00
            net_pay=1693.50,             # 2143.50 - 450.00 = 1693.50
            ytd_gross=15000.00
        )
        res = self.analyzer.analyze_structured_data(data)
        self.assertEqual(res.risk_level, "LOW RISK")
        self.assertEqual(res.risk_score, 0)

    def test_03_legit_executive_high_pay(self):
        """Carol: $10,000 monthly gross with itemized federal and state tax."""
        data = PaystubData(
            gross_pay=10000.00,
            social_security_tax=620.00,  # 10000 * 0.062 = 620.00
            medicare_tax=145.00,         # 10000 * 0.0145 = 145.00
            federal_income_tax=1535.00,
            state_income_tax=500.00,
            total_deductions=2800.00,    # 620 + 145 + 1535 + 500 = 2800.00
            net_pay=7200.00,             # 10000 - 2800 = 7200.00
            ytd_gross=80000.00
        )
        res = self.analyzer.analyze_structured_data(data)
        self.assertEqual(res.risk_level, "LOW RISK")
        self.assertEqual(res.risk_score, 0)

    # --- FORGERY PROFILES (Expected: HIGH RISK, Score >= 50) ---

    def test_04_fraud_rounded_social_security(self):
        """Fake Generator: Rounded Social Security tax ($150 instead of $279)."""
        data = PaystubData(
            gross_pay=4500.00,
            social_security_tax=150.00,  # Fraud: Expected $279.00
            medicare_tax=65.25,          # Correct
            total_deductions=800.00,
            net_pay=3700.00,
            ytd_gross=18000.00
        )
        res = self.analyzer.analyze_structured_data(data)
        self.assertEqual(res.risk_level, "HIGH RISK")
        self.assertGreaterEqual(res.risk_score, 40)
        flag_codes = [f.code for f in res.red_flags]
        self.assertIn("MATH_FICA_SS_MISMATCH", flag_codes)

    def test_05_fraud_fabricated_medicare(self):
        """Fake Generator: Made up Medicare tax ($25 instead of $58)."""
        data = PaystubData(
            gross_pay=4000.00,
            social_security_tax=248.00,  # Correct
            medicare_tax=25.00,          # Fraud: Expected $58.00
            total_deductions=800.00,
            net_pay=3200.00,
            ytd_gross=16000.00
        )
        res = self.analyzer.analyze_structured_data(data)
        self.assertEqual(res.risk_level, "HIGH RISK")
        flag_codes = [f.code for f in res.red_flags]
        self.assertIn("MATH_FICA_MEDICARE_MISMATCH", flag_codes)

    def test_06_fraud_altered_net_pay(self):
        """Photoshop Tamper: Applicant edited Net Pay from $3,000 to $4,500 without adjusting deductions."""
        data = PaystubData(
            gross_pay=5000.00,
            social_security_tax=310.00,
            medicare_tax=72.50,
            total_deductions=2000.00,
            net_pay=4500.00,             # Fraud: 5000 - 2000 = 3000, NOT 4500!
            ytd_gross=25000.00
        )
        res = self.analyzer.analyze_structured_data(data)
        self.assertEqual(res.risk_level, "HIGH RISK")
        flag_codes = [f.code for f in res.red_flags]
        self.assertIn("MATH_NET_PAY_FORMULA_BROKEN", flag_codes)

    def test_07_fraud_impossible_ytd(self):
        """Spliced Stub: YTD Gross ($1,000) is less than current period Gross ($3,000)."""
        data = PaystubData(
            gross_pay=3000.00,
            social_security_tax=186.00,
            medicare_tax=43.50,
            total_deductions=600.00,
            net_pay=2400.00,
            ytd_gross=1000.00            # Impossible
        )
        res = self.analyzer.analyze_structured_data(data)
        self.assertEqual(res.risk_level, "HIGH RISK")
        flag_codes = [f.code for f in res.red_flags]
        self.assertIn("MATH_YTD_LESS_THAN_CURRENT", flag_codes)

    def test_08_fraud_compound_discrepancy(self):
        """Multiple Failures: Wrong SS, Wrong Net Pay, Broken Math."""
        data = PaystubData(
            gross_pay=6000.00,
            social_security_tax=200.00,  # Off by $172
            medicare_tax=30.00,          # Off by $57
            total_deductions=1000.00,
            net_pay=5500.00,             # Math broken (should be 5000)
            ytd_gross=12000.00
        )
        res = self.analyzer.analyze_structured_data(data)
        self.assertEqual(res.risk_level, "HIGH RISK")
        self.assertGreaterEqual(res.risk_score, 80)
        self.assertGreaterEqual(len(res.red_flags), 3)

    # --- PDF FORENSIC PROFILE TESTS ---

    def test_09_pdf_forensics_photoshop_signature(self):
        """Synthetic PDF with Photoshop Producer and Canva Creator."""
        synthetic_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj\n"
            b"<< /Title (Paystub) /Creator (Canva Design Suite) /Producer (Adobe Photoshop CC 2024) >>\n"
            b"endobj\n"
            b"xref\n0 2\n0000000000 65535 f \n0000000010 00000 n \n"
            b"trailer\n<< /Size 2 /Info 1 0 R >>\n"
            b"startxref\n120\n"
            b"%%EOF\n"
        )
        res = self.analyzer.analyze_bytes(synthetic_pdf, filename="test_canva_photoshop.pdf")
        self.assertEqual(res.risk_level, "HIGH RISK")
        flag_codes = [f.code for f in res.red_flags]
        self.assertTrue(any("SUSPICIOUS_SOFTWARE" in code for code in flag_codes))

    def test_10_pdf_forensics_incremental_edit(self):
        """Synthetic PDF containing multiple %%EOF sections (incremental modification)."""
        synthetic_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj << /Type /Catalog >> endobj\n"
            b"xref\n0 2\n0000000000 65535 f \n0000000010 00000 n \n"
            b"trailer << /Size 2 >>\nstartxref\n60\n%%EOF\n"
            b"2 0 obj << /Type /Info /ModDate (D:20261005120000) >> endobj\n"
            b"xref\n2 1\n0000000120 00000 n \n"
            b"trailer << /Size 3 /Prev 60 >>\nstartxref\n180\n%%EOF\n"
        )
        res = self.analyzer.analyze_bytes(synthetic_pdf, filename="test_resaved_pdf.pdf")
        flag_codes = [f.code for f in res.red_flags]
        self.assertIn("PDF_INCREMENTAL_UPDATE_DETECTED", flag_codes)


if __name__ == "__main__":
    unittest.main()
