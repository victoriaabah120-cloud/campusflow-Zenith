import unittest

from campusflow.tickets import TicketError, calculate_priority, create_ticket


class PriorityTests(unittest.TestCase):
    def test_ordered_priority_rules(self):
        cases = (
            ("high", 12, "critical"),
            ("high", 2, "high"),
            ("low", 12, "high"),
            ("medium", 1, "medium"),
            ("low", 4, "medium"),
            ("low", 1, "low"),
        )
        for urgency, users, expected in cases:
            with self.subTest(urgency=urgency, users=users):
                self.assertEqual(calculate_priority(urgency, users), expected)


class TicketCreationTests(unittest.TestCase):
    def test_creates_exact_required_fields_and_normalizes_choices(self):
        ticket = create_ticket([], "  Wi-Fi outage  ", "nEtWoRk", "HIGH", "12")

        self.assertEqual(
            ticket,
            {
                "id": "T001",
                "title": "Wi-Fi outage",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            },
        )

    def test_rejects_invalid_fields_without_mutating_existing_tickets(self):
        tickets = [{"id": "T004"}]
        invalid_inputs = (
            {"title": "  "},
            {"category": "Facilities"},
            {"urgency": "urgent"},
            {"affected_users": 0},
            {"affected_users": -1},
            {"affected_users": 2.5},
            {"affected_users": "2.5"},
            {"affected_users": "many"},
            {"affected_users": "9" * 5000},
            {"affected_users": True},
        )
        for override in invalid_inputs:
            arguments = {
                "title": "Printer issue",
                "category": "Hardware",
                "urgency": "low",
                "affected_users": 1,
            }
            arguments.update(override)
            with self.subTest(override=override):
                with self.assertRaises(TicketError):
                    create_ticket(tickets, **arguments)
                self.assertEqual(tickets, [{"id": "T004"}])

    def test_id_uses_highest_existing_number_not_collection_length(self):
        tickets = [{"id": "T003"}, {"id": "T011"}, {"id": "T007"}]

        ticket = create_ticket(tickets, "Account access", "Software", "low", 1)

        self.assertEqual(ticket["id"], "T012")


if __name__ == "__main__":
    unittest.main()