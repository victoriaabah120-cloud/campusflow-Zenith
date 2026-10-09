# CampusFlow

CampusFlow is a standard-library Python command-line helpdesk for recording,
prioritizing, assigning, and tracking campus technical-support tickets. Priority
is calculated deterministically from urgency and the number of affected users.

## Features

- Create tickets with validated fields and automatically generated `T001`
  style IDs.
- List all tickets or view an individual ticket by ID.
- Assign unresolved tickets to staff members.
- Move tickets through `open`, `in_progress`, and `resolved`, with explicit
  reopening for resolved work.
- View an unresolved queue ordered by critical, high, medium, and low priority,
  then by the numeric ticket ID.
- View totals and counts by status and priority.
- Persist and validate tickets in JSON, using atomic file replacement on save.

## Contributors

The assignment requires two fellows and partner review. Names and individual
contributions must be entered by the actual fellows; none are inferred here.

| Fellow | Name | Verified contribution |
| --- | --- | --- |
| Engineer A | [Enter Fellow A's name] | [Complete from actual authored work and review] |
| Engineer B | [Enter Fellow B's name] | [Complete from actual authored work and review] |

The implementation in this workspace is on local branch
`feat/1-ticket-creation`. No fellow-authored commits, pull requests, partner
reviews, or approvals are claimed by this README. The second fellow should use
the contribution workflow in [docs/design-decisions.md](docs/design-decisions.md)
and complete their own learning log.

## Requirements

- Python 3.9 or newer; no third-party packages are required.
- Run commands from the repository root.

## Setup and Run

Clone the repository and enter its directory, then check Python:

```sh
python3 --version
```

Start the interactive CLI:

```sh
python3 main.py
```

CampusFlow creates `data/tickets.json` on the first successful state change.
The `data/` directory is created automatically. If no JSON file exists at
startup, the application starts with an empty ticket collection. Invalid or
malformed existing data is reported and is never replaced with an empty file.

## Menu

On startup, CampusFlow displays a branded header and a live dashboard with the
total, open, in-progress, and resolved ticket counts. Ticket lists use aligned
columns; long values are shortened in tables with a note, and full text remains
available in ticket details.

1. Create a new ticket.
2. View all tickets.
3. View ticket details.
4. Assign a ticket to a staff member.
5. Update a ticket to `in_progress` or `resolved`.
6. View the open-ticket queue (all unresolved tickets).
7. View reports.
8. Reopen a resolved ticket.
9. Exit the application.

Invalid menu selections display guidance and return to the menu. Invalid ticket
creation fields are explained and prompted again. Other rejected operations
display an error and return to the menu. Exiting does not rewrite ticket data;
successful changes are saved as they happen.

## Ticket Rules

Each ticket contains `id`, `title`, `category`, `urgency`, `affected_users`,
`priority`, `status`, and `assigned_to`. Titles and staff names cannot be blank.
Categories are Network, Hardware, Software, and Other; urgency is low, medium,
or high. Case variations are accepted and stored in canonical form.
`affected_users` must be a positive whole number; zero, negative values,
decimals, non-numeric text, and Boolean values are rejected.

Priority is calculated in this order:

1. High urgency and at least 10 affected users: `critical`.
2. Otherwise, high urgency or at least 10 affected users: `high`.
3. Otherwise, medium urgency or at least 3 affected users: `medium`.
4. Otherwise: `low`.

New tickets start as `open`. An unassigned ticket cannot enter `in_progress`.
An assigned ticket may move from `open` to `in_progress`, then to `resolved`.
Resolved tickets cannot be assigned or changed through ordinary status updates;
use menu option 6 to explicitly reopen one to `open` first.

The unresolved queue includes `open` and `in_progress` tickets, excludes
`resolved` tickets, and sorts by priority rank (critical, high, medium, low),
then ascending numeric ID. Reports include all tickets and zero-valued counts
for every status and priority, including when the collection is empty.

## Storage and Safety

The default store is `data/tickets.json`, resolved relative to `main.py` rather
than the current working directory. Startup validates the complete collection,
including unique IDs and consistency between priority, urgency, and affected
users. Missing files mean an empty collection; empty, malformed, or invalid
files raise a clear error without being overwritten. Successful writes use a
temporary file in the same directory and atomic replacement. Runtime ticket
data is excluded from Git.

## Tests

Run the standard-library test suite from the repository root:

```sh
python -m unittest discover -s tests -v
```

Tests cover priority decisions, validation, IDs, assignment and status rules,
queue order, empty and populated reports, persistence and reload, malformed
data, and interactive CLI flows. Persistence tests use temporary directories.

## Demonstration

1. Run the test command above.
2. Run `python3 main.py` and create a Network ticket with high urgency and 12
	affected users; confirm its priority is critical.
3. List and view the ticket, assign a staff member, then move it to
	`in_progress` and `resolved`.
4. Display the queue and reports; confirm resolved tickets are excluded from
	the queue and included in reports.
5. Reopen the ticket, exit, restart CampusFlow, and view it to demonstrate
	persistence. Create a second ticket and confirm its ID is unique.
6. For the malformed-data check, use a separate temporary JSON path with
	invalid content in a test or isolated copy; startup must report the error
	without altering that file.

## Known Limitations and Submission Status

This is a single-user local CLI with a JSON file, not a multi-user service.
Concurrent writers, authentication, ticket deletion, and editing ticket
details are out of scope. This workspace does not establish that the required
two-person branch/PR/review/approval workflow is complete. Add genuine fellow
names, contribution summaries, reviewed PR links, learning evidence, and review
results before treating the assignment submission as complete.

Pull request A: [Add real reviewed PR URL]

Pull request B: [Add real reviewed PR URL]