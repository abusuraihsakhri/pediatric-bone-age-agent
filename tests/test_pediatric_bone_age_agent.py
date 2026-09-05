"""
Automated Pytest Test Suite for Pediatric Bone Age Agent.
Domain: Radiology & Neuroimaging Systems
Standard: ACR RADS / Fleischner Society / ASPECTS Guidelines
"""
import os
import sys
from pathlib import Path

# Set required environment variable BEFORE importing agents
os.environ.setdefault("AUDIT_SECRET_KEY", "test-audit-secret-key-for-unit-tests-2026")

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_metric_validation_rejects_nan():
    """Ensure NaN metric values are rejected by validation."""
    import math
    with pytest.raises(ValueError, match="finite"):
        SystemTaskPayload(task_id="T-NAN", target_identifier="KEY", primary_metric=math.nan)


def test_metric_validation_rejects_infinity():
    """Ensure infinity metric values are rejected by validation."""
    import math
    with pytest.raises(ValueError, match="finite"):
        SystemTaskPayload(task_id="T-INF", target_identifier="KEY", primary_metric=math.inf)


def test_identifier_validation_rejects_path_traversal():
    """Ensure path traversal characters are rejected in identifiers."""
    with pytest.raises(ValueError, match="path traversal"):
        SystemTaskPayload(task_id="../etc/passwd", target_identifier="KEY", primary_metric=1.0)

    with pytest.raises(ValueError, match="path traversal"):
        SystemTaskPayload(task_id="T1", target_identifier="..\\windows\\system32", primary_metric=1.0)


def test_audit_secret_key_required():
    """Ensure AuditTrail requires a secret key."""
    from agents.base import AuditTrail
    # Clear any existing env var to test the error
    original = os.environ.pop("AUDIT_SECRET_KEY", None)
    try:
        trail = AuditTrail()
        with pytest.raises(SecurityException, match="AUDIT_SECRET_KEY"):
            _ = trail.secret_key
    finally:
        if original:
            os.environ["AUDIT_SECRET_KEY"] = original


def test_audit_secret_key_minimum_length():
    """Ensure short secret keys are rejected."""
    from agents.base import AuditTrail
    trail = AuditTrail(secret_key="short")
    with pytest.raises(SecurityException, match="at least 16"):
        _ = trail.secret_key
