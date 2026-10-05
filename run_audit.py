#!/usr/bin/env python3
"""
TenantGuard AI - CLI Audit Tool.
Usage:
    python3 run_audit.py --demo
    python3 run_audit.py --file path/to/paystub.pdf [--format json|markdown|terminal]
"""
import sys
import os
import argparse

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import TenantGuardAnalyzer, ReportGenerator, PaystubData


def run_demo():
    print("\nRunning TenantGuard AI Demo on 4 synthetic applicant test cases...\n")
    analyzer = TenantGuardAnalyzer()

    # Case 1: Legitimate Compliant Paystub (Clean Tech Worker)
    case_legit = PaystubData(
        employer_name="Acme Corp Solutions LLC",
        employee_name="Alice Walker",
        gross_pay=4000.00,
        social_security_tax=248.00,  # 4000 * 0.062 = 248.00 (Exact)
        medicare_tax=58.00,          # 4000 * 0.0145 = 58.00 (Exact)
        federal_income_tax=450.00,
        state_income_tax=180.00,
        other_deductions=64.00,
        total_deductions=1000.00,    # 248 + 58 + 450 + 180 + 64 = 1000.00
        net_pay=3000.00,             # 4000 - 1000 = 3000.00
        ytd_gross=24000.00
    )
    res_1 = analyzer.analyze_structured_data(case_legit, filename="applicant_alice_legit_adp.pdf")
    ReportGenerator.print_terminal(res_1)

    # Case 2: Blatant FICA Tax Math Forgery (Online generator rounded FICA)
    case_math_fraud = PaystubData(
        employer_name="Apex Logistics Inc",
        employee_name="Robert Smith",
        gross_pay=5000.00,
        social_security_tax=180.00,  # FAKE: should be 5000 * 0.062 = 310.00! Discrepancy $130!
        medicare_tax=40.00,          # FAKE: should be 5000 * 0.0145 = 72.50! Discrepancy $32.50!
        total_deductions=800.00,
        net_pay=4200.00,
        ytd_gross=15000.00
    )
    res_2 = analyzer.analyze_structured_data(case_math_fraud, filename="applicant_robert_fake_math.pdf")
    ReportGenerator.print_terminal(res_2)

    # Case 3: Net Pay Calculation Failure (Photoshop modified numbers)
    case_photoshop = PaystubData(
        employer_name="Global Retail Partners",
        employee_name="John Doe",
        gross_pay=6500.00,
        social_security_tax=403.00,  # Correct
        medicare_tax=94.25,          # Correct
        total_deductions=1500.00,
        net_pay=5500.00,             # BROKEN MATH: 6500 - 1500 should be 5000, but modified to 5500!
        ytd_gross=32000.00
    )
    res_3 = analyzer.analyze_structured_data(case_photoshop, filename="applicant_john_altered_netpay.pdf")
    ReportGenerator.print_terminal(res_3)

    # Case 4: Impossible YTD Number (Spliced from another person's document)
    case_ytd = PaystubData(
        employer_name="Sunrise Marketing",
        employee_name="David Vance",
        gross_pay=3200.00,
        social_security_tax=198.40,
        medicare_tax=46.40,
        total_deductions=600.00,
        net_pay=2600.00,
        ytd_gross=1200.00            # IMPOSSIBLE: YTD is LESS than single pay period!
    )
    res_4 = analyzer.analyze_structured_data(case_ytd, filename="applicant_david_impossible_ytd.pdf")
    ReportGenerator.print_terminal(res_4)


def main():
    parser = argparse.ArgumentParser(description="TenantGuard AI - Forensic Paystub & Document Verification")
    parser.add_argument("--file", "-f", help="Path to PDF paystub to analyze")
    parser.add_argument("--demo", action="store_true", help="Run synthetic demonstration test cases")
    parser.add_argument("--format", choices=["terminal", "markdown", "json"], default="terminal", help="Output format")
    parser.add_argument("--out", "-o", help="Optional output file path")

    args = parser.parse_args()

    if args.demo or not args.file:
        run_demo()
        return

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)

    with open(args.file, "rb") as f:
        file_bytes = f.read()

    analyzer = TenantGuardAnalyzer()
    result = analyzer.analyze_bytes(file_bytes, filename=os.path.basename(args.file))

    if args.format == "terminal":
        ReportGenerator.print_terminal(result)
    elif args.format == "markdown":
        output = ReportGenerator.to_markdown(result)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as out_f:
                out_f.write(output)
            print(f"Report saved to {args.out}")
        else:
            print(output)
    elif args.format == "json":
        output = ReportGenerator.to_json(result)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as out_f:
                out_f.write(output)
            print(f"JSON saved to {args.out}")
        else:
            print(output)


if __name__ == "__main__":
    main()
