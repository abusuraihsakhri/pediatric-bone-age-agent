"""Tests for signed audit logs, API comparison and CSV boolean parsing."""
import pytest

from agents.base import AuditTrail
from cli import parse_csv_bool as parse_root_bool
from pediatric_bone_age_agent.cli import parse_csv_bool as parse_package_bool
from fastapi.testclient import TestClient
from agents.api import app


def test_hmac_detects_value_tampering():
    trail = AuditTrail(secret_key="a-long-ci-test-audit-key")
    trail.log("tester", "test", "FIRST", {"value": 1})
    trail.log("tester", "test", "SECOND", {"value": 2})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "ALTERED"
    assert not trail.verify_integrity()


def test_hmac_detects_last_entry_tampering():
    trail = AuditTrail(secret_key="a-long-ci-test-audit-key")
    trail.log("tester", "test", "ONE", {"value": 1})
    trail.logs[0]["current_hash"] = "f" * 64
    assert not trail.verify_integrity()


@pytest.mark.parametrize("parser", [parse_root_bool, parse_package_bool])
@pytest.mark.parametrize("text,expected", [
    ("True", True), ("TRUE", True), ("1", True),
    ("false", False), ("0", False), ("", False), ("No", False),
])
def test_csv_boolean(parser, text, expected):
    assert parser(text) is expected


@pytest.mark.parametrize("parser", [parse_root_bool, parse_package_bool])
def test_invalid_boolean_rejected(parser):
    with pytest.raises(ValueError):
        parser("not-a-bool")


def test_compare_api():
    client = TestClient(app)
    response = client.post("/api/bone-age/compare", json={
        "chronological_age_months": 120,
        "bone_age_months": 132,
        "assessment_method": "Greulich-Pyle",
    })
    assert response.status_code == 200, response.text
    assert response.json()["difference_months"] == 12
    assert response.json()["direction"] == "advanced"


def test_compare_api_rejects_invalid():
    client = TestClient(app)
    response = client.post("/api/bone-age/compare", json={
        "chronological_age_months": -3,
        "bone_age_months": 130,
    })
    assert response.status_code == 422


def test_compare_cli(capsys):
    from pediatric_bone_age_agent.cli import main
    assert main(["compare", "--chronological-months", "120",
                 "--bone-months", "114"]) == 0
    captured = capsys.readouterr().out
    assert '"difference_months": -6.0' in captured
