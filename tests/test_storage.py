import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket


class StorageTests(unittest.TestCase):
    def test_missing_file_starts_empty_and_save_reload_preserves_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data" / "tickets.json"
            self.assertEqual(load_tickets(path), [])

            tickets = [create_ticket([], "Wi-Fi outage", "Network", "high", 12)]
            save_tickets(tickets, path)
            reloaded = load_tickets(path)

            self.assertEqual(reloaded, tickets)
            next_ticket = create_ticket(reloaded, "Printer issue", "Hardware", "low", 1)
            self.assertEqual(next_ticket["id"], "T002")

    def test_malformed_json_is_reported_and_original_file_is_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            original = "{ this is not JSON\n"
            path.write_text(original, encoding="utf-8")

            with self.assertRaisesRegex(StorageError, "malformed JSON"):
                load_tickets(path)

            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_empty_file_and_invalid_structure_are_not_treated_as_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(StorageError, "malformed JSON"):
                load_tickets(path)

            path.write_text(json.dumps({"tickets": []}), encoding="utf-8")
            with self.assertRaisesRegex(StorageError, "JSON array"):
                load_tickets(path)

    def test_duplicate_or_inconsistent_persisted_records_are_rejected(self):
        ticket = create_ticket([], "Wi-Fi outage", "Network", "high", 12)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text(json.dumps([ticket, ticket]), encoding="utf-8")
            with self.assertRaisesRegex(StorageError, "Duplicate ticket ID"):
                load_tickets(path)

            inconsistent = ticket.copy()
            inconsistent["priority"] = "low"
            path.write_text(json.dumps([inconsistent]), encoding="utf-8")
            with self.assertRaisesRegex(StorageError, "inconsistent"):
                load_tickets(path)

            zero_id = ticket.copy()
            zero_id["id"] = "T000"
            path.write_text(json.dumps([zero_id]), encoding="utf-8")
            with self.assertRaisesRegex(StorageError, "invalid ID"):
                load_tickets(path)

            unassigned = ticket.copy()
            unassigned["status"] = "in_progress"
            path.write_text(json.dumps([unassigned]), encoding="utf-8")
            with self.assertRaisesRegex(StorageError, "without an assignee"):
                load_tickets(path)

    def test_invalid_save_does_not_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text("existing data", encoding="utf-8")

            with self.assertRaises(StorageError):
                save_tickets([{"id": "T001"}], path)

            self.assertEqual(path.read_text(encoding="utf-8"), "existing data")

    def test_atomic_replace_failure_preserves_store_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            original = '[{"existing": true}]\n'
            path.write_text(original, encoding="utf-8")
            tickets = [create_ticket([], "Wi-Fi outage", "Network", "high", 12)]

            with patch(
                "campusflow.storage.os.replace",
                side_effect=OSError("simulated replace failure"),
            ):
                with self.assertRaisesRegex(StorageError, "simulated replace failure"):
                    save_tickets(tickets, path)

            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(Path(directory).glob(".tickets.json.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()