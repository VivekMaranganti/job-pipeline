---
name: batch-prep-apply
description: Tailor resumes and fill applications for MULTIPLE targets, one at a time in strict sequence, stopping each before final submit. Pass a comma-separated list of company names, Notion rows, or posting URLs, or omit it to process every Notion row currently "Not Started".
disable-model-invocation: true
context: fork
agent: batch-apply-prepper
background: true
argument-hint: "[optional: comma-separated targets; omit to process all 'Not Started' rows]"
---

Prepare these applications end to end, one at a time in strict sequence,
never in parallel: $ARGUMENTS

If a target list is given (comma-separated company names, Notion rows, or
posting URLs), process exactly those targets in the order given. If no
targets are given, query Notion for every row with `Application Status` set
to `Not Started` and process all of them.

For each target: resolve the posting, tailor the resume, fill out the
application form, stop before submitting, update the Notion row, and move to
the next target. If a target hits a hard blocker, log it and move on rather
than stopping the batch. When the queue is done, report a summary of the
batch so I can review before I send anything.
