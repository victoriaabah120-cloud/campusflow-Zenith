import unittest

from campusflow.reports import build_report
from campusflow.tickets import create_ticket


class ReportTests(unittest.TestCase):
    def test_empty_collection_has_all_zero_counts(self):
        self.assertEqual(
            build_report([]),
            {
                "total": 0,
                "by_status": {"open": 0, "in_progress": 0, "resolved": 0},
                "by_priority": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                },
            },
        )

    def test_non_empty_counts_match_ticket_collection(self):
        tickets = [
            create_ticket([], "Network outage", "Network", "high", 12),
            create_ticket([], "Slow login", "Software", "medium", 1),
            create_ticket([], "Printer setup", "Hardware", "low", 1),
        ]
        tickets[1]["status"] = "in_progress"
        tickets[2]["status"] = "resolved"

        self.assertEqual(
            build_report(tickets),
            {
                "total": 3,
                "by_status": {"open": 1, "in_progress": 1, "resolved": 1},
                "by_priority": {"critical": 1, "high": 0, "medium": 1, "low": 1},
            },
        )

    def test_report_counts_add_up_to_total(self):
        tickets = [
            create_ticket([], "Network outage", "Network", "high", 12),
            create_ticket([], "Slow login", "Software", "medium", 1),
            create_ticket([], "Printer setup", "Hardware", "low", 1),
        ]

        report = build_report(tickets)

        self.assertEqual(
            sum(report["by_status"].values()),
            report["total"],
        )
        self.assertEqual(
            sum(report["by_priority"].values()),
            report["total"],
        )

if __name__ == "__main__":
    unittest.main()