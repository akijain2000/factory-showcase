---
name: s02-research-synthesis
description: Evaluates source quality, normalizes citations, and merges findings across references. Use when claims conflict, evidence depth varies, or agent 02-research-assistant requires a shared synthesis method.
---

# Research synthesis from multiple sources

## Goal / overview

Rank and reconcile information from several sources so conclusions stay traceable. Covers credibility checks, a compact citation shape, and written synthesis that flags agreement, tension, and gaps. Pairs with agent `02-research-assistant`.

## When to use

- Two or more sources address the same question with different emphasis or conclusions.
- A deliverable must show where each claim comes from without burying the reader in URLs.
- The research assistant needs repeatable rules for weighting blogs, papers, docs, and primary data.

## Steps

1. **Classify each source**: identify type (peer-reviewed, official vendor doc, community post, primary dataset, opinion), date, scope, and whether the author has direct access to the subject matter.
2. **Score reliability for this task**: note known limitations (paywall abstracts only, translation, marketing copy) and downgrade weight when methodology or data is invisible.
3. **Extract atomic claims**: one finding per bullet, each tagged with source id; separate fact from interpretation in the notes column.
4. **Normalize citations**: pick one format (e.g. short in-line key plus a reference list with title, publisher/host, date retrieved, stable URL or DOI). Apply it to every claim.
5. **Synthesize**: group by theme; for each theme state (a) convergent evidence, (b) single-source-only points labeled as such, (c) direct conflicts with both sides cited.
6. **State residual uncertainty**: list what would change the conclusion if better evidence appeared.

## Output format

- **Source table**: id, type, relevance (high/medium/low), reliability notes, citation line.
- **Claim matrix**: claim text, supporting source ids, contradicting source ids (or "none").
- **Synthesis sections**: themed paragraphs or bullets with inline source keys.
- **Open questions**: bullet list tied to missing or weak evidence.

## Gotchas

- Recency matters for APIs and product behavior; an old tutorial can disagree with current vendor docs—check dates before merging.
- Duplicate URLs with different titles still count as one source unless content materially differs.
- Secondary summaries of a paper are not substitutes for the primary text when precision matters.

## Test scenarios

1. **Conflicting benchmarks**: Two blog posts report different latency numbers for the same library; output should rank sources, cite both, and explain which measurement context is more comparable.
2. **Thin evidence**: One official doc plus three forum threads; synthesis should mark forum-only claims clearly and avoid presenting them as vendor guarantees.
3. **Citation cleanup**: Raw notes mix bare URLs and informal names; output should produce a consistent reference list and inline keys without losing traceability.
