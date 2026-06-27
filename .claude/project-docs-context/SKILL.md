---
name: project-docs-context
description: Loads and maintains the project's `docs/` folder as persistent context across Claude Code sessions. Use ALWAYS at the start of any session in a repo that has `docs/`, `documentation/`, or `.docs/` — read it FIRST so work is grounded in the PRDs, plans, architecture notes, and business-logic descriptions there. Also use whenever you create, edit, rename, or delete any file inside docs/ — update the index and changelog so the next session can pick up the trail. Triggers include "продолжим работу", "что у нас по проекту", "let's continue", "review the project", or simply the implicit start of work in a repo that has a docs folder. If you're about to write a PRD, plan, design doc, ADR, or business-logic description, route it through this skill so it lands in docs/ and the index gets updated. Do NOT skip just because the user didn't mention "docs" — the docs folder is the project's memory and should load automatically.
---

# Project Docs Context

This skill makes the `docs/` folder of a project act as durable, structured memory across Claude Code sessions. Two responsibilities:

1. **On session start** — load the docs so you have project context before doing any real work.
2. **On any docs change** — update the index and changelog so the next session can pick up the trail.

---

## 1. Session start: load the docs

Run this at the very beginning of a session in any repo that has a docs folder. Do it before answering the user's first substantive question (unless they explicitly ask for something that has nothing to do with the project, like a generic "what's 2+2").

### Step 1.1 — Locate the docs folder

Check these paths in order, stop at the first that exists:

1. `./docs/`
2. `./documentation/`
3. `./.docs/`

```bash
for d in docs documentation .docs; do
  if [ -d "$d" ]; then echo "FOUND: $d"; break; fi
done
```

If none exist, this skill is done — there are no docs to load. Don't create the folder yourself unless the user asks for it.

### Step 1.2 — Read the index first (cheap path)

If `<docs>/README.md` or `<docs>/index.md` exists, read it in full. That's the curated entry point — it should tell you what's in the folder and how it's organized.

After reading the index, you have two options depending on what the index promises:

- **Index covers everything you need** (it summarizes each doc): you're done with loading. Mention briefly to the user what's in scope ("I've loaded the project docs — I see the PRD for X, the plan for Y, and ADRs about Z. What are we working on?").
- **Index is light or missing entries**: list the remaining files and read the ones that look load-bearing (PRD, plan, architecture, current-state notes). Skip stale-looking files (e.g., `notes-from-2023-brainstorm.md`) unless relevant.

### Step 1.3 — No index? Build a map

If there's no README/index inside docs/, do this:

```bash
find <docs> -type f \( -name "*.md" -o -name "*.mdx" \) | sort
```

For each file, read the first ~30 lines (enough to see the title and intro) to understand its purpose. Then read in full the files that look load-bearing for the current work.

Common load-bearing names: `PRD*`, `*plan*`, `architecture*`, `ARCHITECTURE*`, `*design*`, `STATE*`, `*business-logic*`, `*entities*`, `decisions/*`, `adr/*`.

### Step 1.4 — Confirm context loaded

Briefly tell the user what you loaded — one or two sentences, not a wall of summary. Example:

> Loaded `docs/`: PRD v2 for the billing module, the current sprint plan, and 3 ADRs on the database choice. Ready when you are.

Don't dump the contents back at the user — they wrote it. Just confirm what's now in scope.

---

## 2. On any docs change: maintain the index and changelog

Whenever you create, edit, rename, or delete a file under `docs/` during a session, do the bookkeeping below. This is what makes the docs folder durable memory rather than a write-only log.

### Step 2.1 — Update `docs/README.md` (the index)

If `docs/README.md` doesn't exist, create it with this structure:

```markdown
# Project Documentation

This folder is the project's persistent context: PRDs, plans, architecture notes, business-logic descriptions, and decision records. Claude reads this at the start of every session.

## Contents

- [PRD: <feature>](./PRD-<feature>.md) — <one-line description>
- [Plan: <thing>](./plan-<thing>.md) — <one-line description>
- [Architecture](./architecture.md) — <one-line description>

## Conventions

- New PRDs go in `docs/` with prefix `PRD-`.
- Decision records (ADRs) go in `docs/decisions/` numbered sequentially.
- Plans go in `docs/` with prefix `plan-`.
- Update this README whenever you add, rename, or delete a doc.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for chronological doc changes.
```

When adding/renaming/deleting a doc, edit the **Contents** section accordingly. Keep entries to one line. Don't duplicate the doc's content here — just point at it.

### Step 2.2 — Append to `docs/CHANGELOG.md`

If it doesn't exist, create it:

```markdown
# Documentation Changelog

Chronological log of documentation changes. Most recent at the top.
```

For each docs change in the current session, prepend an entry:

```markdown
## YYYY-MM-DD

- **Added** `docs/PRD-billing.md` — initial PRD for the billing rework.
- **Updated** `docs/plan-q2.md` — added milestone 3, removed obsolete frontend rewrite section.
- **Renamed** `docs/old-arch.md` → `docs/architecture-v1.md` (archived; superseded by `architecture.md`).
- **Deleted** `docs/scratch-notes.md` (merged into PRD-billing.md).
```

Use today's date as a header. If today's date already has a section, append under it instead of creating a duplicate.

### Step 2.3 — Get the current date

Don't hardcode dates. Use:

```bash
date +%Y-%m-%d
```

### Step 2.4 — Batch the bookkeeping

If you're making many docs changes in one session, you don't need to update the index and changelog after every single file. Do it once near the end of the session, or when the user signals they're winding down. The goal is that the next session-start read of `docs/README.md` reflects reality.

---

## Edge cases

**The repo has no docs/ folder.** Don't create one preemptively. If the user starts asking you to plan or write a PRD, then create `docs/` and seed it with `README.md` + `CHANGELOG.md` from the templates above.

**The docs folder has hundreds of files.** Don't read all of them. Use the index. If there's no index, build one as your first action (sample the structure with `find` and `head`), then propose to the user that you commit a `README.md` to make future sessions faster.

**Conflicting docs (e.g., two PRDs that disagree).** Note the conflict to the user. Don't silently pick one. Suggest resolving by either updating the older one or marking it `superseded`.

**Docs folder contains non-markdown files** (diagrams, PDFs, images). Note them in the index but don't try to read binary content unless asked. For PDFs, mention that they're available if the user wants details extracted.

**User says "don't load docs this time."** Respect that. Skip the load step for the current session.

---

## What this skill is NOT

- Not a replacement for `CLAUDE.md` at the repo root. `CLAUDE.md` is for Claude-Code-specific instructions (coding conventions, commands to run). `docs/` is for the product/project itself.
- Not a search index. Don't try to build embeddings or anything fancy. Plain markdown + a curated README is the system.
- Not retroactive. If the project already has docs but no README/CHANGELOG, this skill will create them on first use — it doesn't try to reconstruct history that wasn't logged.