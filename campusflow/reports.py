"""Ticket count summaries."""

from .tickets import PRIORITIES, STATUSES


def build_report(tickets):
    """Return total, status counts, and priority counts for the collection."""
    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITIES}

    for ticket in tickets:
        by_status[ticket["status"]] += 1
        by_priority[ticket["priority"]] += 1

    return {
        "total": len(tickets),
        "by_status": by_status,
        "by_priority": by_priority,
    }