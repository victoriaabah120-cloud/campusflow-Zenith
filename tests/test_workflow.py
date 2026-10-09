import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    WorkflowError,
    assign_ticket,
    reopen_ticket,
    unresolved_queue,
    update_ticket_status,
)


def make_ticket(ticket_id, urgency="low", users=1, status="open", assigned_to=None):
    ticket = create_ticket([], ticket_id, "Other", urgency, users)
    ticket["id"] = ticket_id
    ticket["status"] = status
    ticket["assigned_to"] = assigned_to
    return ticket


class WorkflowTests(unittest.TestCase):
    def test_assignment_rejects_unknown_ids_and_blank_names(self):
        tickets = [make_ticket("T001")]
        original = tickets[0].copy()

        with self.assertRaisesRegex(WorkflowError, "No ticket found"):
            assign_ticket(tickets, "T999", "Casey")
        with self.assertRaisesRegex(WorkflowError, "cannot be blank"):
            assign_ticket(tickets, "T001", "  ")

        self.assertEqual(tickets[0], original)

    def test_assignment_and_forward_status_workflow(self):
        tickets = [make_ticket("T001")]

        with self.assertRaisesRegex(WorkflowError, "Assign the ticket"):
            update_ticket_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "open")

        assign_ticket(tickets, "T001", "  Jordan Lee  ")
        update_ticket_status(tickets, "T001", "IN_PROGRESS")
        update_ticket_status(tickets, "T001", "resolved")

        self.assertEqual(tickets[0]["assigned_to"], "Jordan Lee")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_invalid_transitions_and_resolved_changes_are_rejected(self):
        tickets = [make_ticket("T001", assigned_to="Jordan")]

        for status in ("open", "resolved", "paused"):
            with self.subTest(status=status):
                with self.assertRaises(WorkflowError):
                    update_ticket_status(tickets, "T001", status)
        self.assertEqual(tickets[0]["status"], "open")

        update_ticket_status(tickets, "T001", "in_progress")
        update_ticket_status(tickets, "T001", "resolved")
        resolved_copy = tickets[0].copy()
        with self.assertRaisesRegex(WorkflowError, "reopened"):
            assign_ticket(tickets, "T001", "Taylor")
        with self.assertRaisesRegex(WorkflowError, "reopened"):
            update_ticket_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0], resolved_copy)

        reopen_ticket(tickets, "T001")
        self.assertEqual(tickets[0]["status"], "open")

    def test_reopen_requires_resolved_ticket_and_unknown_ids_are_clear(self):
        tickets = [make_ticket("T001")]

        with self.assertRaisesRegex(WorkflowError, "Only resolved"):
            reopen_ticket(tickets, "T001")
        with self.assertRaisesRegex(WorkflowError, "No ticket found"):
            reopen_ticket(tickets, "T404")

    def test_queue_priority_then_numeric_id_and_unresolved_only(self):
        tickets = [
            make_ticket("T010", "high", 2, "open"),
            make_ticket("T002", "high", 2, "in_progress"),
            make_ticket("T020", "high", 12, "resolved", "Jordan"),
            make_ticket("T005", "low", 4, "open"),
            make_ticket("T003", "low", 1, "in_progress", "Casey"),
        ]

        queue = unresolved_queue(tickets)

        self.assertEqual([ticket["id"] for ticket in queue], [
            "T002", "T010", "T005", "T003"
        ])
        self.assertNotIn("T020", [ticket["id"] for ticket in queue])


if __name__ == "__main__":
    unittest.main()