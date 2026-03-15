import pytest
from bson.objectid import ObjectId

import src.api as api
from src.database import mongo_client


@pytest.fixture
def bug_report(request):
    report = api.create_bug_report(api.BugReportRequest(**request.param))
    yield report
    mongo_client["game_db"]["bug_reports"].delete_one({"_id": ObjectId(report["id"])})


@pytest.mark.parametrize("bug_report", [
    {"game_id": "abc123", "turn": 5, "description": "Pawn disappeared after capture", "region": "America/New_York"}
], indirect=True)
def test_bug_report_with_description(bug_report):
    assert "id" in bug_report
    assert bug_report["game_id"] == "abc123"
    assert bug_report["turn"] == 5
    assert bug_report["description"] == "Pawn disappeared after capture"
    assert bug_report["region"] == "America/New_York"
    assert "timestamp" in bug_report


@pytest.mark.parametrize("bug_report", [
    {"game_id": "def456", "turn": 12}
], indirect=True)
def test_bug_report_with_empty_description(bug_report):
    assert "id" in bug_report
    assert bug_report["game_id"] == "def456"
    assert bug_report["turn"] == 12
    assert bug_report["description"] == ""
    assert bug_report["region"] == ""
    assert "timestamp" in bug_report
