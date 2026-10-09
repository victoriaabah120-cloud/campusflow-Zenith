"""Interactive command-line entry point for CampusFlow."""

import copy
from pathlib import Path

from campusflow.reports import build_report
from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import TicketError, create_ticket
from campusflow.workflow import (
    WorkflowError,
    assign_ticket,
    get_ticket,
    reopen_ticket,
    unresolved_queue,
    update_ticket_status,
)


DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "tickets.json"
WIDTH = 24
TABLE_COLUMNS = (
    ("Ticket ID", "id", 7),
    ("Title", "title", 16),
    ("Category", "category", 9),
    ("Priority", "priority", 8),
    ("Status", "status", 12),
    ("Assigned staff", "assigned_to", 14),
)
QUEUE_COLUMNS = (
    TABLE_COLUMNS[0],
    TABLE_COLUMNS[1],
    TABLE_COLUMNS[3],
    TABLE_COLUMNS[4],
    TABLE_COLUMNS[5],
)


class _InputEnded(Exception):
    """Signal that the user ended input during a prompt."""


def _read_input(input_fn, prompt):
    try:
        return input_fn(prompt)
    except (EOFError, KeyboardInterrupt) as error:
        raise _InputEnded from error


def _prompt_ticket_field(input_fn, output_fn, prompt, guidance, validate):
    while True:
        output_fn(guidance)
        value = _read_input(input_fn, prompt)
        try:
            validate(value)
        except TicketError as error:
            output_fn(f"Invalid input: {error}")
            output_fn("Please correct this field and try again.")
        else:
            return value


def _save_change(tickets, storage_path, change):
    previous_tickets = copy.deepcopy(tickets)
    try:
        result = change()
        save_tickets(tickets, storage_path)
        return result
    except Exception:
        tickets[:] = previous_tickets
        raise


def _section(output_fn, title):
    output_fn(f"\n{title}")
    output_fn("-" * min(len(title), WIDTH))


def _print_header(output_fn):
    output_fn("CampusFlow")
    output_fn("IT Service Desk")


def _status_label(status):
    return status.replace("_", " ").title()


def _ticket_cell(ticket, field):
    value = ticket[field]
    if field == "priority":
        return value.title()
    if field == "status":
        return _status_label(value)
    if field == "urgency":
        return value.title()
    if field == "assigned_to":
        return value or "Unassigned"
    return str(value)


def _display_table(tickets, output_fn, columns=TABLE_COLUMNS):
    heading = "  ".join(label.ljust(width) for label, _, width in columns)
    rule = "  ".join("-" * width for _, _, width in columns)
    output_fn(heading)
    output_fn(rule)

    truncated = False
    for ticket in tickets:
        cells = []
        for _, field, width in columns:
            value = _ticket_cell(ticket, field)
            if len(value) > width:
                value = value[: width - 3] + "..."
                truncated = True
            cells.append(value.ljust(width))
        output_fn("  ".join(cells))

    if truncated:
        output_fn(
            "Note: Long values are shortened to fit the table. "
            "View ticket details for the complete text."
        )


def _display_ticket(ticket, output_fn):
    _section(output_fn, "TICKET DETAILS")
    details = (
        ("Ticket ID", ticket["id"]),
        ("Title", ticket["title"]),
        ("Category", ticket["category"]),
        ("Urgency", ticket["urgency"].title()),
        ("Affected users", str(ticket["affected_users"])),
        ("Calculated priority", ticket["priority"].title()),
        ("Current status", _status_label(ticket["status"])),
        ("Assigned staff member", ticket["assigned_to"] or "Unassigned"),
    )
    for label, value in details:
        output_fn(f"{label:<26}: {value}")


def _display_dashboard(tickets, output_fn):
    report = build_report(tickets)
    _section(output_fn, "DASHBOARD")
    output_fn(
        f"Total: {report['total']} | Open: {report['by_status']['open']}"
    )
    output_fn(
        f"In Progress: {report['by_status']['in_progress']} | "
        f"Resolved: {report['by_status']['resolved']}"
    )


def _show_menu(output_fn):
    _section(output_fn, "MAIN MENU")
    output_fn("1. Create ticket       2. List tickets")
    output_fn("3. Ticket details      4. Assign ticket")
    output_fn("5. Update status       6. Open queue")
    output_fn("7. Reports             8. Reopen ticket")
    output_fn("9. Exit")


def _display_reports(tickets, output_fn):
    report = build_report(tickets)
    _section(output_fn, "TICKET REPORTS")
    output_fn(f"Total tickets: {report['total']}")
    if not tickets:
        output_fn("There are currently no tickets to report.")

    _section(output_fn, "COUNTS BY STATUS")
    for status, count in report["by_status"].items():
        output_fn(f"{_status_label(status):<16} {count:>6}")

    _section(output_fn, "COUNTS BY PRIORITY")
    for priority, count in report["by_priority"].items():
        output_fn(f"{priority.title():<16} {count:>6}")


def main(storage_path=None, input_fn=None, output_fn=None):
    """Run the menu until exit; return 1 if stored data cannot be loaded."""
    input_fn = input if input_fn is None else input_fn
    output_fn = print if output_fn is None else output_fn
    storage_path = DEFAULT_DATA_PATH if storage_path is None else Path(storage_path)

    _print_header(output_fn)
    try:
        tickets = load_tickets(storage_path)
    except StorageError as error:
        _section(output_fn, "STARTUP ERROR")
        output_fn(f"Unable to load saved tickets: {error}")
        output_fn("Check the JSON file and restart CampusFlow. The file was not changed.")
        return 1

    _display_dashboard(tickets, output_fn)
    _show_menu(output_fn)
    while True:
        try:
            choice = _read_input(input_fn, "Choose an option (1-9): ").strip()
        except _InputEnded:
            output_fn("\nExiting CampusFlow. No additional changes were made.")
            return 0

        try:
            if choice == "1":
                _section(output_fn, "CREATE A NEW TICKET")
                output_fn("Enter each required field. Accepted choices are shown below.")
                title = _prompt_ticket_field(
                    input_fn,
                    output_fn,
                    "Title (required): ",
                    "Title: short summary of the issue, for example 'Wi-Fi outage'.",
                    lambda value: create_ticket([], value, "Other", "low", 1),
                )
                category = _prompt_ticket_field(
                    input_fn,
                    output_fn,
                    "Category: ",
                    "Category: choose Network, Hardware, Software, or Other.",
                    lambda value: create_ticket([], title, value, "low", 1),
                )
                urgency = _prompt_ticket_field(
                    input_fn,
                    output_fn,
                    "Urgency: ",
                    "Urgency: low, medium, or high based on service impact.",
                    lambda value: create_ticket([], title, category, value, 1),
                )
                affected_users = _prompt_ticket_field(
                    input_fn,
                    output_fn,
                    "Number of affected users: ",
                    "Affected users: positive whole number, for example 3.",
                    lambda value: create_ticket(
                        tickets, title, category, urgency, value
                    ),
                )
                ticket = create_ticket(
                    tickets, title, category, urgency, affected_users
                )
                _save_change(
                    tickets,
                    storage_path,
                    lambda: tickets.append(ticket),
                )
                _section(output_fn, "TICKET CREATED")
                output_fn(f"Ticket ID: {ticket['id']}")
                output_fn(f"Title: {ticket['title']}")
                output_fn(f"Calculated priority: {ticket['priority'].title()}")
                output_fn(f"Status: {_status_label(ticket['status'])}")
                output_fn("The ticket was saved successfully.")
            elif choice == "2":
                _section(output_fn, "ALL TICKETS")
                if not tickets:
                    output_fn("There are currently no tickets.")
                else:
                    _display_table(tickets, output_fn)
            elif choice == "3":
                ticket = get_ticket(
                    tickets, _read_input(input_fn, "Ticket ID: ").strip()
                )
                _display_ticket(ticket, output_fn)
            elif choice == "4":
                ticket_id = _read_input(input_fn, "Ticket ID: ").strip()
                ticket = get_ticket(tickets, ticket_id)
                _display_ticket(ticket, output_fn)
                output_fn("Assign this ticket to a staff member using their name.")
                staff_name = _read_input(input_fn, "Staff member name: ")
                ticket = _save_change(
                    tickets,
                    storage_path,
                    lambda: assign_ticket(tickets, ticket_id, staff_name),
                )
                output_fn(
                    f"Success: ticket {ticket['id']} is assigned to "
                    f"{ticket['assigned_to']}."
                )
            elif choice == "5":
                ticket_id = _read_input(input_fn, "Ticket ID: ").strip()
                ticket = get_ticket(tickets, ticket_id)
                _display_ticket(ticket, output_fn)
                if ticket["status"] == "resolved":
                    output_fn("This ticket is resolved. Choose option 8 to reopen it first.")
                elif ticket["status"] == "open" and ticket["assigned_to"] is None:
                    output_fn("Assign this ticket before moving it to In Progress.")
                else:
                    allowed_status = (
                        "In Progress" if ticket["status"] == "open" else "Resolved"
                    )
                    output_fn(f"Allowed next status: {allowed_status}.")
                    status = _read_input(input_fn, "New status (in_progress/resolved): ")
                    ticket = _save_change(
                        tickets,
                        storage_path,
                        lambda: update_ticket_status(tickets, ticket_id, status),
                    )
                    output_fn(
                        f"Success: ticket {ticket['id']} status is now "
                        f"{_status_label(ticket['status'])}."
                    )
            elif choice == "6":
                _section(output_fn, "OPEN-TICKET QUEUE")
                output_fn("Unresolved tickets, ordered by priority then ticket ID.")
                queue = unresolved_queue(tickets)
                if not queue:
                    output_fn("There are no unresolved tickets in the queue.")
                else:
                    _display_table(queue, output_fn, QUEUE_COLUMNS)
            elif choice == "7":
                _display_reports(tickets, output_fn)
            elif choice == "8":
                ticket_id = _read_input(input_fn, "Ticket ID: ").strip()
                ticket = get_ticket(tickets, ticket_id)
                _display_ticket(ticket, output_fn)
                ticket = _save_change(
                    tickets,
                    storage_path,
                    lambda: reopen_ticket(tickets, ticket_id),
                )
                output_fn(f"Success: ticket {ticket['id']} is now Open.")
            elif choice == "9":
                output_fn("Goodbye. All successful changes have already been saved.")
                return 0
            else:
                output_fn("Invalid menu selection. Enter a number from 1 to 9.")
        except TicketError as error:
            _section(output_fn, "INPUT ERROR")
            output_fn(str(error))
            output_fn("Correct the field values and select the operation again.")
        except WorkflowError as error:
            _section(output_fn, "WORKFLOW ERROR")
            output_fn(str(error))
            output_fn("Check the ticket ID and allowed action, then try again.")
        except StorageError as error:
            _section(output_fn, "STORAGE ERROR")
            output_fn(str(error))
            output_fn("The change was not saved. Check the data path and permissions.")
        except _InputEnded:
            output_fn("\nExiting CampusFlow. No incomplete change was saved.")
            return 0

        _show_menu(output_fn)


if __name__ == "__main__":
    raise SystemExit(main())