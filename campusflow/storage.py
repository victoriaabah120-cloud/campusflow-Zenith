"""Validated JSON persistence for CampusFlow tickets."""

import json
import os
import re
import tempfile
from pathlib import Path

from .tickets import CATEGORIES, STATUSES, URGENCIES, TicketError, calculate_priority


REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
}


class StorageError(ValueError):
    """Raised when persisted ticket data cannot safely be read or written."""


def _validate_collection(tickets):
    if not isinstance(tickets, list):
        raise StorageError("Ticket data must be a JSON array.")

    seen_ids = set()
    for index, ticket in enumerate(tickets):
        location = f"Ticket at index {index}"
        if not isinstance(ticket, dict):
            raise StorageError(f"{location} must be a JSON object.")
        missing = REQUIRED_FIELDS - ticket.keys()
        if missing:
            raise StorageError(
                f"{location} is missing required fields: {', '.join(sorted(missing))}."
            )

        ticket_id = ticket["id"]
        if (
            not isinstance(ticket_id, str)
            or not re.fullmatch(r"T[0-9]{3,}", ticket_id)
            or not ticket_id[1:].strip("0")
        ):
            raise StorageError(f"{location} has an invalid ID; expected T001 format.")
        if ticket_id in seen_ids:
            raise StorageError(f"Duplicate ticket ID {ticket_id!r} in stored data.")
        seen_ids.add(ticket_id)

        if not isinstance(ticket["title"], str) or not ticket["title"].strip():
            raise StorageError(f"{location} has a blank or invalid title.")
        if ticket["category"] not in CATEGORIES:
            raise StorageError(f"{location} has an invalid category.")
        if ticket["urgency"] not in URGENCIES:
            raise StorageError(f"{location} has an invalid urgency.")
        users = ticket["affected_users"]
        if isinstance(users, bool) or not isinstance(users, int) or users <= 0:
            raise StorageError(f"{location} has an invalid affected_users value.")
        if ticket["priority"] not in ("critical", "high", "medium", "low"):
            raise StorageError(f"{location} has an invalid priority.")
        try:
            expected_priority = calculate_priority(ticket["urgency"], users)
        except TicketError as error:
            raise StorageError(f"{location} is invalid: {error}") from error
        if ticket["priority"] != expected_priority:
            raise StorageError(f"{location} has a priority inconsistent with its inputs.")
        if ticket["status"] not in STATUSES:
            raise StorageError(f"{location} has an invalid status.")
        assigned_to = ticket["assigned_to"]
        if assigned_to is not None and (
            not isinstance(assigned_to, str) or not assigned_to.strip()
        ):
            raise StorageError(f"{location} has an invalid assigned_to value.")
        if ticket["status"] != "open" and assigned_to is None:
            raise StorageError(
                f"{location} cannot be {ticket['status']} without an assignee."
            )


def load_tickets(path):
    """Load and validate records, returning an empty collection if absent."""
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as ticket_file:
            tickets = json.load(ticket_file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise StorageError(
            f"Cannot load {path}: malformed JSON at line {error.lineno}, "
            f"column {error.colno}."
        ) from error
    except (OSError, UnicodeError) as error:
        raise StorageError(f"Cannot read ticket data from {path}: {error}") from error

    _validate_collection(tickets)
    return tickets


def save_tickets(tickets, path):
    """Atomically write a validated ticket collection as JSON."""
    _validate_collection(tickets)
    path = Path(path)
    temporary_path = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(tickets, temporary_file, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, path)
    except OSError as error:
        raise StorageError(f"Cannot save ticket data to {path}: {error}") from error
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass