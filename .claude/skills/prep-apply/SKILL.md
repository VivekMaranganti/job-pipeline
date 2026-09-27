---
name: prep-apply
description: Tailor the resume and fill out one specific job application in the browser, stopping before final submit. Pass a company name, Notion row, or posting URL.
disable-model-invocation: true
context: fork
agent: apply-prepper
background: true
argument-hint: "<company name, Notion row, or posting URL>"
---

Prepare this application end to end: $ARGUMENTS

Resolve the posting, tailor the resume, fill out the application form, stop
before submitting, update the Notion row, and report back exactly what's
filled in so I can review it before I send it.
