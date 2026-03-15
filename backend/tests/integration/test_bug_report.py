from bson.objectid import ObjectId

import src.api as api
from src.database import mongo_client


def test_bug_report_with_description():
    report = api.create_bug_report(api.BugReportRequest(
        game_id="abc123",
        turn=5,
        description="Pawn disappeared after capture",
        region="America/New_York"
    ))

    try:
        assert "id" in report
        assert report["game_id"] == "abc123"
        assert report["turn"] == 5
        assert report["description"] == "Pawn disappeared after capture"
        assert report["region"] == "America/New_York"
        assert "timestamp" in report
    finally:
        mongo_client["game_db"]["bug_reports"].delete_one({"_id": ObjectId(report["id"])})


def test_bug_report_with_empty_description():
    report = api.create_bug_report(api.BugReportRequest(
        game_id="def456",
        turn=12
    ))

    try:
        assert "id" in report
        assert report["game_id"] == "def456"
        assert report["turn"] == 12
        assert report["description"] == ""
        assert report["region"] == ""
        assert "timestamp" in report
    finally:
        mongo_client["game_db"]["bug_reports"].delete_one({"_id": ObjectId(report["id"])})
