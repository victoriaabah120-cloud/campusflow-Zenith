# AI Learning Log

This file is an evidence template, not evidence that learning interactions or
experiments have happened. Each fellow must fill entries from their own actual
work. Do not count suggested questions, generated code, or another person's
experience as a completed interaction. At least three meaningful entries per
fellow are required, including one where a suggestion was independently
corrected, improved, or rejected after verification.

## Suggested Learning Questions and Experiments

These are prompts for future real investigations, not completed log entries:

- Why does `bool` need explicit rejection when Python also treats it as an
  integer? Experiment in a small Python REPL with `isinstance(True, int)` and
  the validation test in `tests/test_tickets.py`.
- What is the difference between using list length and the maximum numeric ID
  when records contain gaps? Try a separate list with IDs T002 and T009 and
  inspect `generate_ticket_id` behavior.
- Why must a resolved ticket be reopened explicitly? Try each transition in
  `tests/test_workflow.py` and compare the collection before and after rejected
  operations.
- How does same-directory `os.replace` help protect persisted data? Make a
  temporary-file experiment in a temporary directory and inspect the target
  after a deliberately failed write. Never experiment on real ticket data.

## Fellow A

Name: [Enter actual name]

### Interaction 1

- Concept/topic: [Complete]
- Problem investigated: [Complete]
- Initial understanding: [Complete]
- Actual AI prompt: [Paste the real prompt]
- Guidance received: [Summarize accurately]
- Independent experiment or test: [Describe what you ran]
- Actual result/source: [Record output or file/test reference]
- Decision and explanation: [Complete]
- Related file, test, commit, or PR: [Complete]
- What I can explain independently now: [Complete]

### Interaction 2

- Concept/topic: [Complete]
- Problem investigated: [Complete]
- Initial understanding: [Complete]
- Actual AI prompt: [Paste the real prompt]
- Guidance received: [Summarize accurately]
- Independent experiment or test: [Describe what you ran]
- Actual result/source: [Record output or file/test reference]
- Decision and explanation: [Complete]
- Related file, test, commit, or PR: [Complete]
- What I can explain independently now: [Complete]

### Interaction 3 (include a verified correction/rejection)

- Concept/topic: [Complete]
- Problem investigated: [Complete]
- Initial understanding: [Complete]
- Actual AI prompt: [Paste the real prompt]
- Guidance received: [Summarize accurately]
- Independent experiment or test: [Describe what you ran]
- Actual result/source: [Record output or file/test reference]
- Suggestion corrected, improved, or rejected and why: [Complete from evidence]
- Related file, test, commit, or PR: [Complete]
- What I can explain independently now: [Complete]

## Fellow B

Name: [Enter actual name]

### Interaction 1

- Concept/topic: [Complete]
- Problem investigated: [Complete]
- Initial understanding: [Complete]
- Actual AI prompt: [Paste the real prompt]
- Guidance received: [Summarize accurately]
- Independent experiment or test: [Describe what you ran]
- Actual result/source: [Record output or file/test reference]
- Decision and explanation: [Complete]
- Related file, test, commit, or PR: [Complete]
- What I can explain independently now: [Complete]

### Interaction 2

- Concept/topic: [Complete]
- Problem investigated: [Complete]
- Initial understanding: [Complete]
- Actual AI prompt: [Paste the real prompt]
- Guidance received: [Summarize accurately]
- Independent experiment or test: [Describe what you ran]
- Actual result/source: [Record output or file/test reference]
- Decision and explanation: [Complete]
- Related file, test, commit, or PR: [Complete]
- What I can explain independently now: [Complete]

### Interaction 3 (include a verified correction/rejection)

- Concept/topic: [Complete]
- Problem investigated: [Complete]
- Initial understanding: [Complete]
- Actual AI prompt: [Paste the real prompt]
- Guidance received: [Summarize accurately]
- Independent experiment or test: [Describe what you ran]
- Actual result/source: [Record output or file/test reference]
- Suggestion corrected, improved, or rejected and why: [Complete from evidence]
- Related file, test, commit, or PR: [Complete]
- What I can explain independently now: [Complete]