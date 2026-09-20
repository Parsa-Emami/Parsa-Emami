"""Run with:  python -m unittest discover -s tests -v"""
import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_contributions as fc  # noqa: E402

# Markup copied from what github.com/users/<login>/contributions returns today.
FIXTURE = """
<table><tbody><tr>
<td tabindex="0" data-ix="0" style="width: 11px" data-date="2026-06-05" id="contribution-day-component-5-37" data-level="1" role="gridcell" class="ContributionCalendar-day"></td>
<td tabindex="0" data-ix="1" style="width: 11px" data-date="2026-06-06" id="contribution-day-component-6-37" data-level="0" role="gridcell" class="ContributionCalendar-day"></td>
<td tabindex="0" data-ix="2" style="width: 11px" data-date="2026-06-07" id="contribution-day-component-0-38" data-level="4" role="gridcell" class="ContributionCalendar-day"></td>
<td tabindex="0" data-ix="3" style="width: 11px" data-date="2026-06-08" id="no-tooltip-cell" data-level="2" role="gridcell" class="ContributionCalendar-day"></td>
</tr></tbody></table>
<tool-tip for="contribution-day-component-5-37" class="sr-only">1 contribution on June 5th.</tool-tip>
<tool-tip for="contribution-day-component-6-37" class="sr-only">No contributions on June 6th.</tool-tip>
<tool-tip for="contribution-day-component-0-38" class="sr-only">1,204 contributions on June 7th.</tool-tip>
"""


class ParseCalendar(unittest.TestCase):
    def test_counts_from_tooltips(self):
        days = fc.parse_calendar_html(FIXTURE)
        self.assertEqual(days["2026-06-05"], 1)
        self.assertEqual(days["2026-06-06"], 0)
        self.assertEqual(days["2026-06-07"], 1204)  # thousands separator handled

    def test_level_fallback_when_tooltip_missing(self):
        self.assertEqual(fc.parse_calendar_html(FIXTURE)["2026-06-08"], fc.LEVEL_FALLBACK[2])

    def test_raises_when_markup_changes(self):
        with self.assertRaises(RuntimeError):
            fc.parse_calendar_html("<div>nothing here</div>")


class Merge(unittest.TestCase):
    def test_max_not_sum_between_sources(self):
        start, end = dt.date(2026, 9, 1), dt.date(2026, 9, 3)
        cal_a = {"2026-09-01": 2, "2026-09-02": 0}
        cal_b = {"2026-09-01": 1}                      # second account, summed with the first
        commits = {"2026-09-01": 2, "2026-09-02": 5, "2026-09-03": 1}
        days = fc.merge(start, end, [cal_a, cal_b], commits)
        self.assertEqual([d["count"] for d in days], [3, 5, 1])

    def test_streaks(self):
        end = dt.date(2026, 9, 5)
        counts = [0, 2, 1, 0, 3]  # Sep 1..5
        days = [{"date": (dt.date(2026, 9, 1) + dt.timedelta(days=i)).isoformat(), "count": c} for i, c in enumerate(counts)]
        self.assertEqual(fc.current_streak(days, end), 1)
        self.assertEqual(fc.longest_streak(days), 2)
        days[-1]["count"] = 0  # today empty -> streak counts back from yesterday
        self.assertEqual(fc.current_streak(days, end), 0)

    def test_bot_detection(self):
        self.assertTrue(fc._is_bot({"author": {"login": "github-actions[bot]"}}))
        self.assertTrue(fc._is_bot({"author": None, "commit": {"author": {"name": "github-actions"}}}))
        self.assertFalse(fc._is_bot({"author": {"login": "parsaemm", "type": "User"}, "commit": {"author": {"name": "parsaemm"}}}))


if __name__ == "__main__":
    unittest.main()
