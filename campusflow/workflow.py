"""Ticket assignment, status transitions, and work queue operations."""

from .tickets import PRIORITIES, STATUSES


class WorkflowError(ValueError):
    """Raised when a requested ticket workflow operation is not allowed."""


def _find_ticket(tickets, ticket_id):
    for ticket in tickets:
        if ticket.get("id") == ticket_id:
            return ticket
    raise WorkflowError(f"No ticket found with ID {ticket_id!r}.")


def get_ticket(tickets, ticket_id):
    """Return one ticket by ID or raise a clear workflow error."""
    return _find_ticket(tickets, ticket_id)


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign an unresolved ticket to a non-empty staff member name."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise WorkflowError("Staff member name cannot be blank.")
    ticket = _find_ticket(tickets, ticket_id)
    if ticket["status"] == "resolved":
        raise WorkflowError("Resolved tickets must be reopened before reassignment.")

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def update_ticket_status(tickets, ticket_id, requested_status):
    """Apply an allowed forward status transition to a ticket."""
    if not isinstance(requested_status, str):
        raise WorkflowError(f"Status must be one of: {', '.join(STATUSES)}.")
    status = requested_status.strip().casefold()
    if status not in STATUSES:
        raise WorkflowError(f"Invalid status. Choose one of: {', '.join(STATUSES)}.")

    ticket = _find_ticket(tickets, ticket_id)
    current_status = ticket["status"]
    if current_status == "resolved":
        raise WorkflowError("Resolved tickets must be explicitly reopened first.")
    if current_status == "open" and status == "in_progress":
        if ticket["assigned_to"] is None:
            raise WorkflowError("Assign the ticket before moving it to in_progress.")
    elif current_status == "in_progress" and status == "resolved":
        pass
    else:
        raise WorkflowError(
            f"Cannot change ticket status from {current_status} to {status}."
        )

    ticket["status"] = status
    return ticket


def reopen_ticket(tickets, ticket_id):
    """Explicitly reopen a resolved ticket."""
    ticket = _find_ticket(tickets, ticket_id)
    if ticket["status"] != "resolved":
        raise WorkflowError("Only resolved tickets can be reopened.")
    ticket["status"] = "open"
    return ticket


def unresolved_queue(tickets):
    """Return unresolved tickets by priority rank, then numeric ticket ID."""
    priority_rank = {priority: index for index, priority in enumerate(PRIORITIES)}
    unresolved = [ticket for ticket in tickets if ticket["status"] != "resolved"]
    return sorted(
        unresolved,
        key=lambda ticket: (priority_rank[ticket["priority"]], int(ticket["id"][1:])),
    )