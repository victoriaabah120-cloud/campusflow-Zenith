"""Ticket validation, priority calculation, and ID generation."""

import re


CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCIES = ("low", "medium", "high")
PRIORITIES = ("critical", "high", "medium", "low")
STATUSES = ("open", "in_progress", "resolved")


class TicketError(ValueError):
    """Raised when ticket input does not meet the application rules."""


def _normalize_choice(value, choices, field_name):
    if not isinstance(value, str):
        raise TicketError(f"{field_name} must be one of: {', '.join(choices)}.")

    normalized = value.strip().casefold()
    for choice in choices:
        if normalized == choice.casefold():
            return choice
    raise TicketError(f"Invalid {field_name}. Choose one of: {', '.join(choices)}.")


def _validate_affected_users(value):
    if isinstance(value, bool):
        raise TicketError("Affected users must be a positive whole number.")
    if isinstance(value, int):
        count = value
    elif isinstance(value, str) and re.fullmatch(r"[+]?[0-9]+", value.strip()):
        try:
            count = int(value.strip())
        except ValueError as error:
            raise TicketError(
                "Affected users must be a positive whole number."
            ) from error
    else:
        raise TicketError("Affected users must be a positive whole number.")

    if count <= 0:
        raise TicketError("Affected users must be greater than zero.")
    return count


def calculate_priority(urgency, affected_users):
    """Return priority using the specified ordered business rules."""
    urgency = _normalize_choice(urgency, URGENCIES, "urgency")
    affected_users = _validate_affected_users(affected_users)

    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def generate_ticket_id(tickets):
    """Generate the next ID after the highest existing numeric ticket ID."""
    highest_id = 0
    for ticket in tickets:
        ticket_id = ticket.get("id")
        if isinstance(ticket_id, str):
            match = re.fullmatch(r"T([0-9]+)", ticket_id)
            if match:
                highest_id = max(highest_id, int(match.group(1)))
    return f"T{highest_id + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate inputs and return a new ticket without mutating the collection."""
    if not isinstance(title, str) or not title.strip():
        raise TicketError("Title cannot be blank.")

    category = _normalize_choice(category, CATEGORIES, "category")
    urgency = _normalize_choice(urgency, URGENCIES, "urgency")
    affected_users = _validate_affected_users(affected_users)
    priority = calculate_priority(urgency, affected_users)

    return {
        "id": generate_ticket_id(tickets),
        "title": title.strip(),
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }