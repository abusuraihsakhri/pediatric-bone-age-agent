"""
Clinical Algorithmic Engine & Guideline Rules for BoneAge Sentinel: Greulich-Pyle & Tanner-Whitehouse Skeletal Maturity Agent.
Domain: Pediatric Radiology
Standard: Greulich-Pyle & Tanner-Whitehouse Standards
"""
import math
from typing import Dict, Any, List, Optional
from .models import ClinicalCasePayload, AgentAlert, UrgencyLevel, ClinicalIntegrityStatus


class ClinicalDomainEngine:
    GUIDELINE = "Demonstration thresholds; not clinical guidelines"
    PRIMARY_BASELINE_LIMIT = 20.0
    SECONDARY_ALERT_LIMIT = 10.0

    @classmethod
    def evaluate_primary_index(cls, value: float) -> Optional[Dict[str, Any]]:
        if value > cls.PRIMARY_BASELINE_LIMIT:
            return {
                "title": "Primary Metric Threshold Exceeded",
                "finding": f"Observed value ({value:.2f}) exceeds a demonstration-only threshold of ({cls.PRIMARY_BASELINE_LIMIT:.1f}).",
                "recommendation": "Review this demonstration threshold; it is not a validated clinical rule.",
            }
        return None

    @classmethod
    def evaluate_secondary_kinetics(cls, value: float, is_stat: bool) -> Optional[Dict[str, Any]]:
        if value > cls.SECONDARY_ALERT_LIMIT or is_stat:
            return {
                "title": "Demonstration Kinetic Flag Triggered",
                "finding": f"Kinetic parameter ({value:.2f}) with STAT={is_stat} triggered a demonstration status flag.",
                "recommendation": "Demonstration flag only; independently determine any clinical escalation.",
            }
        return None

    @classmethod
    def evaluate_biomarker_concordance(cls, status_flag: str, biomarkers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        status_upper = str(status_flag).upper()
        if "DISCORDANT" in status_upper or "EQUIVOCAL" in status_upper or "MUTANT" in status_upper:
            return {
                "title": "Demonstration Descriptor Flag Matched",
                "finding": f"Status flag '{status_flag}' matched the demonstration rule set; no diagnostic inference is available.",
                "recommendation": f"Review the demonstration descriptor; no clinical decision is supported.",
            }
        return None
