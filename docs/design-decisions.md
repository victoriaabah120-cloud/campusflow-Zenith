# Design Decisions

## Data and Module Boundaries

A ticket is a plain Python dictionary containing the eight required fields:
`id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`,
and `assigned_to`. The collection is a list of these dictionaries. This keeps
the JSON representation direct and makes the core functions easy to exercise
with `unittest`; no database or third-party dependency is needed.

- `main.py` owns menu interaction, prompts, display, startup, and coordination.
- `campusflow/tickets.py` owns input validation, priority calculation, and IDs.
- `campusflow/workflow.py` owns lookup, assignment, status transitions, and queue ordering.
- `campusflow/storage.py` validates and loads/saves JSON data.
- `campusflow/reports.py` calculates totals and grouped counts.
- `tests/` exercises the modules and complete CLI flows.

## Function Contracts and Errors

`create_ticket(tickets, title, category, urgency, affected_users)` returns a
new validated dictionary and does not mutate `tickets`. It raises `TicketError`
for invalid fields. `calculate_priority(urgency, affected_users)` applies the
ordered business rules and raises `TicketError` for invalid inputs.

Workflow functions operate on the list and return the changed ticket. Invalid
IDs, blank assignment names, and disallowed transitions raise `WorkflowError`
before mutation. `reopen_ticket` is the only operation that moves a resolved
ticket back to open. `unresolved_queue` returns a sorted list without modifying
the input collection.

The report tests also verify consistency: the sum of all status counts and
the sum of all priority counts must each equal the total ticket count.
This helps detect discrepancies in report aggregation.

`load_tickets(path)` returns a validated list, or an empty list when the file is
absent. `save_tickets(tickets, path)` validates before writing. Both surface
clear `StorageError` messages for invalid data or I/O failures. The CLI catches
these expected errors and continues; startup load errors exit without entering
the menu. State-changing CLI operations restore their in-memory snapshot if
validation or persistence fails.

`build_report(tickets)` returns a dictionary with `total`, `by_status`, and
`by_priority`; each breakdown always contains every supported label.

## IDs and Persistence

IDs are `T` followed by at least three decimal digits. Generation finds the
largest numeric suffix in the existing collection and returns the next number,
so unsorted tickets and gaps do not cause reuse. Startup rejects malformed or
duplicate IDs instead of trying to repair user data. The collection is stored
at `data/tickets.json`, relative to the project entry point. The parent
directory is created on save. A same-directory temporary file is flushed and
synced before `os.replace` atomically installs it; a failed save leaves the
previous target file in place.

The runtime data file is ignored by Git. Tests use temporary paths, never the
runtime store.

## Team Ownership and Integration

The intended assignment split is Engineer A: ticket creation, validation,
priority, and their tests; Engineer B: assignment, workflow, queue, reports,
and their tests. Both fellows must agree on the dictionary and error contracts
above, integrate storage/CLI work, and make separate feature branches and PRs.


Both fellows should document their actual contributions and collaboration
using their own Git history and pull requests. Engineer A's additional
report-consistency test is recorded in the
`feat/johnson-report-improvement` branch. The test verifies that status
counts and priority counts each sum to the total number of tickets.
The branch was pushed to GitHub for review. Review and merge status must
be confirmed from the pull request before submission.

Before submitting, the actual fellows should:

1. Add their names and real ownership/contribution summaries to the README.
2. Keep each fellow's authored changes on a separate feature branch and open a
   PR linked to a real issue. Include summary, decisions, actual test output,
   edge cases, learning evidence, limitations, and specific reviewer questions.
3. Have each fellow inspect the other's actual code and leave at least two
   substantive observations. Fix genuine defects and obtain approval on the
   final diff; do not self-approve or merge unreviewed changes.
4. Record only genuine AI prompts, experiments, results, decisions, and
   personal learning in `docs/ai-learning-log.md`.

Example branch commands for the second fellow, after coordinating with the
team and fetching the shared base:

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feat/2-workflow-reports
```

Use focused commits such as `feat: enforce ticket status transitions` and
`test: cover unresolved queue ordering`. Do not put runtime ticket data,
credentials, or generated Python files in a PR.


### Report consistency test

- Concept/topic: Unit testing and report consistency.
- Problem investigated: How to verify that ticket report counts are consistent.
- Initial understanding: The existing tests checked expected counts for empty
  and populated ticket collections.
- Actual AI prompt: [Record the actual question you asked about this task.]
- Guidance received: Add a test that checks whether the sum of status counts
  and the sum of priority counts each equal the total number of tickets.
- Independent experiment or test: Ran
  `python -m unittest discover -s tests -v`.
- Actual result/source: All 27 tests passed, including
  `test_report_counts_add_up_to_total`.
- Decision and explanation: Added the consistency test to
  `tests/test_reports.py` and committed the change.
- Related file, test, commit, or PR: `tests/test_reports.py`;
  commit `b9b0710`; branch `feat/johnson-report-improvement`.
- What I can explain independently now: How assertions can verify that
  grouped report counts agree with the overall ticket total.