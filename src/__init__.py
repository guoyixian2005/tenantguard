"""
TenantGuard AI - Pure-Python Paystub Fraud Detection Core.
"""
from .models import PaystubData, VerificationResult, RedFlag, RiskSeverity
from .analyzer import TenantGuardAnalyzer
from .report_generator import ReportGenerator

__all__ = ["PaystubData", "VerificationResult", "RedFlag", "RiskSeverity", "TenantGuardAnalyzer", "ReportGenerator"]
