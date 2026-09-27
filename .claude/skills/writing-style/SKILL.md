---
name: writing-style
description: Plain, direct writing standard for everything this project writes on the user's behalf. Consult it before finalizing resume bullets, application free-text answers, cover letters, and summaries, to strip AI-sounding phrasing, hedging, and padded structure. resume-tailoring and apply-prepper consult it before finalizing wording. Edit this file to match your own voice.
---

# Writing style

The goal is writing that reads like a person wrote it quickly and meant every
word, not writing generated to sound impressive. Recruiters read a lot of
AI-generated application text and discount it. Run prose through this filter
before finalizing it.

This is a default. Edit it to match your own voice.

## The core standard

Every sentence should be **direct, specific, and falsifiable**. If a sentence
could be deleted without losing information, or if it makes a claim too vague
to be wrong, cut or rewrite it.

## Concrete rules

### Cut these outright
- **Em dashes.** Use a period, comma, or colon instead.
- **Hedging that doesn't add real uncertainty**: "it's worth noting that,"
  "in today's fast-paced world," "when it comes to X," "at the end of the day."
  If something is true, say it's true. If it's genuinely uncertain, say what's
  uncertain about it specifically — don't hedge as a reflex.
- **Throat-clearing openers.** Don't warm up before the point — lead with it.
  ("I wanted to reach out to let you know that..." → just say the thing.)
- **Corporate/AI-coded verbs**: "leverage," "utilize," "facilitate," "delve
  into," "unlock," "elevate," "seamless," "robust," "cutting-edge,"
  "game-changing." Use the plain verb: "use," "help," "look into." If a claim
  needs an adjective like "robust" to sound impressive, it needs a specific
  fact instead ("passed 200 tests," not "robustly tested").
- **Padded triads and "not only X but also Y" constructions.** These are a
  reliable AI-writing tell. Say the one thing that's true; don't inflate it
  into three parallel clauses for rhythm.
- **Unnecessary intensifiers**: "very," "really," "truly," "incredibly." If
  the fact is impressive, the fact carries it without an adverb.

### Do these instead
- **Lead with the actual point**, then support it. Don't build up to it.
- **Prefer concrete numbers and specifics over adjectives.** "40x faster" beats
  "significantly faster." "200+ tests" beats "thoroughly tested."
- **Short sentences over long compound ones**, especially for the point that
  matters most in a paragraph.
- **Plain, everyday words.** If a five-dollar word and a common word mean the
  same thing, use the common one.
- **Be decisive when asked for a recommendation.** Give the actual answer, not
  a menu of options with no pick, unless the choice is genuinely ambiguous and
  depends on information Claude doesn't have — in which case ask one clarifying
  question instead of hedging in prose.
- **Name a real gap or problem plainly** rather than softening it into vague
  language. If something is missing, say what's missing, not "there may be
  room for improvement in this area."

## Before / after examples

**Before:** "It's worth noting that this project leverages a robust,
cutting-edge architecture to seamlessly facilitate concurrent request
handling — which not only improves performance but also enhances reliability."

**After:** "This handles concurrent requests with a custom thread pool at the
socket level. It sustains 500 RPS with a p99 latency of 12 ms."

**Before:** "I wanted to let you know that, at the end of the day, there might
be a few areas where the resume could potentially be strengthened, depending
on your priorities."

**After:** "The resume is missing hands-on Java experience, which this JD asks
for directly. That's a real gap, not a wording problem."

**Before:** "You could consider either Option A, which offers certain
advantages, or Option B, which comes with its own tradeoffs, depending on what
matters most to you."

**After:** "Go with Option A. It's faster to ship and the tradeoff (less
flexibility later) doesn't matter for what you're building right now."

## Self-check before finalizing any prose

Before finalizing written output, scan it for:
- [ ] Any em dash — replace it
- [ ] Any sentence that could be deleted with no loss of information — cut it
- [ ] Any adjective doing the work a fact should do — replace with the fact
- [ ] Any hedge that isn't backed by real uncertainty — cut it or make the
      uncertainty specific
- [ ] Any place where a recommendation was asked for but not given — give one
- [ ] Any padded three-part list or "not only/but also" construction — trim
      to the one true claim

This applies to the prose Claude writes in chat, not just documents or files.
