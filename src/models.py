"""
Data models for TenantGuard AI Paystub & Document Verification.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class RiskSeverity(str, Enum):
    LOW = "LOW"            # Green: informative or minor discrepancy
    MEDIUM = "MEDIUM"      # Yellow: questionable, requires manual review
    HIGH = "HIGH"          # Red: strong indicator of fraud or manual alteration
    CRITICAL = "CRITICAL"  # Blatant forgery (known generator, invalid math > 20%)


@dataclass
class RedFlag:
    code: str
    severity: RiskSeverity
    category: str  # "METADATA", "MATHEMATICAL", "LAYOUT", "EMPLOYER"
    title: str
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    suggested_action: str = ""


@dataclass
class PaystubData:
    raw_text: str = ""
    employer_name: Optional[str] = None
    employee_name: Optional[str] = None
    pay_period_start: Optional[str] = None
    pay_period_end: Optional[str] = None
    pay_date: Optional[str] = None
    
    # Financial fields
    gross_pay: Optional[float] = None
    net_pay: Optional[float] = None
    total_deductions: Optional[float] = None
    
    # Statutory Deductions (US)
    social_security_tax: Optional[float] = None
    medicare_tax: Optional[float] = None
    federal_income_tax: Optional[float] = None
    state_income_tax: Optional[float] = None
    other_deductions: Optional[float] = None
    
    # Year-To-Date (YTD)
    ytd_gross: Optional[float] = None
    ytd_net: Optional[float] = None
    ytd_social_security: Optional[float] = None
    ytd_medicare: Optional[float] = None
    ytd_federal_tax: Optional[float] = None


@dataclass
class VerificationResult:
    filename: str
    timestamp: str
    risk_score: int  # 0 to 100 (0=Clean, 100=Confirmed Forgery)
    risk_level: str  # "LOW", "MODERATE", "HIGH"
    red_flags: List[RedFlag] = field(default_factory=list)
    clean_signals: List[str] = field(default_factory=list)
    parsed_data: Optional[PaystubData] = None
    metadata_summary: Dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""
