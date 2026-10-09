import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket
from main import main


class CliTests(unittest.TestCase):
    def test_menu_runs_ticket_lifecycle_and_restores_saved_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            responses = iter(
                [
                    "1", "Campus Wi-Fi is down", "network", "high", "12",
                    "2",
                    "3", "T001",
                    "4", "T001", "Morgan Chen",
                    "5", "T001", "in_progress",
                    "6",
                    "7",
                    "5", "T001", "resolved",
                    "8", "T001",
                    "9",
                ]
            )
            output = []

            result = main(path, input_fn=lambda _prompt: next(responses), output_fn=output.append)
            rendered = "\n".join(output)
            rendered_casefolded = rendered.casefold()

            self.assertEqual(result, 0)
            self.assertIn("CampusFlow", rendered)
            self.assertIn("Calculated priority: critical".casefold(), rendered_casefolded)
            self.assertIn("Total tickets: 1", rendered)
            self.assertIn(
                "Success: ticket T001 is now open".casefold(), rendered_casefolded
            )
            self.assertIn("Success: ticket T001 is assigned to Morgan Chen", rendered)
            self.assertIn(
                "Success: ticket T001 status is now in progress".casefold(),
                rendered_casefolded,
            )
            self.assertIn("OPEN-TICKET QUEUE", rendered)
            self.assertIn("TICKET REPORTS", rendered)
            self.assertIn("in progress", rendered_casefolded)
            saved = load_tickets(path)
            self.assertEqual(saved[0]["assigned_to"], "Morgan Chen")
            self.assertEqual(saved[0]["status"], "open")

    def test_invalid_choice_and_bad_input_do_not_end_menu(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            responses = iter(
                ["0", "1", "  ", "Ticket title", "Network", "high", "0", "1", "9"]
            )
            output = []

            result = main(path, input_fn=lambda _prompt: next(responses), output_fn=output.append)
            rendered = "\n".join(output)

            self.assertEqual(result, 0)
            self.assertIn("Invalid menu selection", rendered)
            self.assertIn("Title cannot be blank", rendered)
            self.assertIn("Affected users must be greater than zero", rendered)
            self.assertIn("TICKET CREATED", rendered)
            self.assertEqual(len(load_tickets(path)), 1)

    def test_malformed_startup_data_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text("not json", encoding="utf-8")
            output = []

            result = main(path, input_fn=lambda _prompt: "9", output_fn=output.append)

            self.assertEqual(result, 1)
            self.assertEqual(path.read_text(encoding="utf-8"), "not json")
            rendered = "\n".join(output)
            self.assertIn("CampusFlow", rendered)
            self.assertIn("Unable to load saved tickets", rendered)
            self.assertIn("The file was not changed", rendered)

    def test_end_of_input_during_ticket_entry_exits_cleanly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            responses = iter(["1"])

            def input_fn(_prompt):
                try:
                    return next(responses)
                except StopIteration as error:
                    raise EOFError from error

            output = []
            result = main(path, input_fn=input_fn, output_fn=output.append)

            self.assertEqual(result, 0)
            self.assertTrue(any("Exiting CampusFlow" in line for line in output))
            self.assertFalse(path.exists())

    def test_failed_save_rolls_back_in_memory_ticket_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            responses = iter(["1", "Network outage", "Network", "high", "12", "9"])
            output = []

            with patch("main.save_tickets", side_effect=StorageError("simulated write failure")):
                result = main(
                    path,
                    input_fn=lambda _prompt: next(responses),
                    output_fn=output.append,
                )

            self.assertEqual(result, 0)
            rendered = "\n".join(output)
            self.assertIn("simulated write failure", rendered)
            self.assertIn("The change was not saved", rendered)
            self.assertFalse(path.exists())

    def test_dashboard_and_menu_are_branded_and_show_zero_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            responses = iter(["7", "9"])
            output = []
            prompts = []

            def input_fn(prompt):
                prompts.append(prompt)
                return next(responses)

            result = main(path, input_fn=input_fn, output_fn=output.append)
            rendered = "\n".join(output)

            self.assertEqual(result, 0)
            self.assertIn("CampusFlow", rendered)
            self.assertIn("IT Service Desk", rendered)
            self.assertIn("Total: 0 | Open: 0", rendered)
            self.assertIn("In Progress: 0 | Resolved: 0", rendered)
            self.assertIn("There are currently no tickets to report.", rendered)
            self.assertRegex(rendered.casefold(), r"critical\s+0")

            menu_labels = (
                "1. Create ticket       2. List tickets",
                "3. Ticket details      4. Assign ticket",
                "5. Update status       6. Open queue",
                "7. Reports             8. Reopen ticket",
                "9. Exit",
            )
            menu_positions = [rendered.index(label) for label in menu_labels]
            self.assertEqual(menu_positions, sorted(menu_positions))
            self.assertIn("Choose an option (1-9): ", prompts)

    def test_creation_retries_invalid_category_and_urgency(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            responses = iter(
                ["1", "Account access", "Facilities", "Software", "urgent", "medium", "2", "9"]
            )
            output = []

            result = main(path, input_fn=lambda _prompt: next(responses), output_fn=output.append)
            rendered = "\n".join(output)

            self.assertEqual(result, 0)
            self.assertIn("Invalid category", rendered)
            self.assertIn("Choose one of: Network, Hardware, Software, Other", rendered)
            self.assertIn("Invalid urgency", rendered)
            self.assertIn("Choose one of: low, medium, high", rendered)
            ticket = load_tickets(path)[0]
            self.assertEqual(ticket["category"], "Software")
            self.assertEqual(ticket["urgency"], "medium")

    def test_ticket_table_aligns_columns_and_explains_truncation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            ticket = create_ticket(
                [], "A very long campus network outage title that exceeds the table width",
                "Network", "high", 12
            )
            ticket["assigned_to"] = "A very long staff member name that exceeds the column"
            save_tickets([ticket], path)
            responses = iter(["2", "3", "T001", "9"])
            output = []

            result = main(path, input_fn=lambda _prompt: next(responses), output_fn=output.append)
            rendered = "\n".join(output)
            table_row = next(line for line in output if line.startswith("T001"))

            self.assertEqual(result, 0)
            self.assertEqual(len(table_row), 76)
            self.assertIn("critical", table_row.casefold())
            self.assertIn("open", table_row.casefold())
            self.assertIn("...", table_row)
            self.assertNotIn("PRIORITY INPUTS", rendered)
            self.assertIn("Long values are shortened", rendered)
            self.assertIn(ticket["title"], rendered)
            self.assertIn("Assigned staff member", rendered)
            self.assertIn("Urgency", rendered)
            self.assertIn("Affected users", rendered)

    def test_unknown_ticket_id_shows_actionable_error_and_returns_to_menu(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            responses = iter(["3", "T999", "9"])
            output = []

            result = main(path, input_fn=lambda _prompt: next(responses), output_fn=output.append)
            rendered = "\n".join(output)

            self.assertEqual(result, 0)
            self.assertIn("No ticket found with ID 'T999'", rendered)
            self.assertIn("Check the ticket ID and allowed action", rendered)
            self.assertGreater(rendered.count("MAIN MENU"), 1)


if __name__ == "__main__":
    unittest.main()