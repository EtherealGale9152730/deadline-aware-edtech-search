from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from edtech_search import educator_report


def test_report_keeps_deadlines_on_or_after_today():
    matches = [{"id": "due-soon", "metadata": {"deadline": "2026-09-01"}}, {"id": "expired", "metadata": {"deadline": "2026-08-31"}}]
    assert educator_report(matches, date(2026, 9, 1)) == {"visible_courses": 1, "course_ids": ["due-soon"]}
