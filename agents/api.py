"""
FastAPI REST API Server for Pediatric Bone Age Agent.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from pediatric_bone_age_agent.comparison import compare_bone_ages

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Pediatric Bone Age Agent API",
    description="Demonstration rule engine and descriptive bone-age comparison; not validated for clinical use.",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "pediatric-bone-age-agent", "domain": "Radiology & Neuroimaging Systems", "mode": "demonstration", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class BoneAgeCompareRequest(BaseModel):
    chronological_age_months: float
    bone_age_months: float
    assessment_method: str = "Unspecified"


@app.post("/api/bone-age/compare")
def api_bone_age_compare(req: BoneAgeCompareRequest):
    try:
        return compare_bone_ages(
            req.chronological_age_months, req.bone_age_months,
            req.assessment_method,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
