"""
FastAPI REST Application & Webhooks for BoneAge Sentinel: Greulich-Pyle & Tanner-Whitehouse Skeletal Maturity Agent.
"""
from typing import Dict, Any, Optional
from .models import ClinicalCasePayload
from .agents import BoneAgeCoordinator
from .comparison import compare_bone_ages

coordinator = BoneAgeCoordinator()

def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel

        app = FastAPI(
            title="BoneAge Sentinel: Greulich-Pyle & Tanner-Whitehouse Skeletal Maturity Agent",
            description="Demonstration alert rules and manual skeletal-age versus chronological-age arithmetic. No radiograph assessment or height prediction.",
            version="2.0.0-PRO",
        )

        class AuditRequest(BaseModel):
            case_id: str = "CASE-2026-001"
            patient_synthetic_id: str = "SYNTH-PT-881"
            primary_metric: float = 24.5
            secondary_metric: float = 14.0
            status_flag: str = "DISCORDANT"
            is_stat: bool = True
            clinical_notes: str = ""
            biomarkers: Dict[str, Any] = {}

        class ChatRequest(BaseModel):
            query: str

        class CompareRequest(BaseModel):
            chronological_age_months: float
            bone_age_months: float
            assessment_method: str = "Unspecified"

        @app.post("/api/bone-age/compare")
        def compare(req: CompareRequest):
            from fastapi import HTTPException
            try:
                return compare_bone_ages(
                    req.chronological_age_months,
                    req.bone_age_months,
                    req.assessment_method,
                )
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "pediatric-bone-age-agent", "domain": "Pediatric Radiology", "version": "2.0.0-PRO"}

        @app.post("/api/audit")
        def api_audit(req: AuditRequest):
            payload = ClinicalCasePayload(
                case_id=req.case_id,
                patient_synthetic_id=req.patient_synthetic_id,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_flag=req.status_flag,
                is_stat=req.is_stat,
                clinical_notes=req.clinical_notes,
                biomarkers=req.biomarkers,
            )
            return coordinator.process_case(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
