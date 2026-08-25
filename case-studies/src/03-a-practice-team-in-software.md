---
slug: a-practice-team-in-software
kind: Working paper
title: A practice team in software
standfirst: The public cut of a working paper for the firm's leadership. A manager model, a worker model and a human partner, with the roles enforced in code rather than requested in a prompt.
date: August 2026
intro: The public version of a working paper I wrote for the leadership of the accountancy firm I build for. The long version, with the architecture, lives on GitHub.
link_label: The full paper on GitHub
link_url: https://github.com/Sanyo4/vedas-pi
---

### The thesis

Accounts preparation already has a good structure. A junior does the legwork. A manager routes the work, reviews it, sends the odd bits back, and takes the real questions upward. A partner makes the calls and signs. Nobody asks the partner to do the bookkeeping.

The system I've been building runs a job the same way. An expensive AI model is the manager: it routes, briefs, reviews and escalates. A cheap model is the worker: conversion, extraction, gathering, at roughly a thirtieth of the price. The human is the partner. They hold the liability, supply the client nuance, and sign.

That's not the novel part. Lots of people draw that diagram. The novel part is this: the structure has to be enforced by the software, in code, because every commercial agent platform I tested let the expensive model do the cheap work when I asked nicely in a prompt, and it always eventually did.

### Why prompts aren't enough

On the first two builds, the rules that mattered were requests. "Delegate extraction to the worker." "Don't read source documents yourself." The telemetry showed those requests breaking under load. The expensive model quietly did the mechanical work itself at about eleven times the input price. Separately, a configuration slip routed cheap work to the expensive model and nothing in any log said so.

A rule the software can break under load is a suggestion. So the third build moved onto a minimal open-source harness where the rules are code the harness runs, not text the model reads. Four enforcement points.

**Delegation by tool denial.** The manager model can't open source documents. It doesn't have the tool. The only path to a figure is dispatching a worker. There's an escape hatch for judgement reads, and it's logged, so an override is visible rather than silent.

**Worker return contracts.** Workers return a fixed summary block and nothing else. Their transcripts are dropped before they can flood the manager's context. A missing block or low confidence becomes a forced escalation to the human. Model slot assignments are checked loudly at startup, because the previous build had silently run cheap work on the expensive model when a reference was wrong.

**Reviewable memory.** Nothing is remembered unless the user approves the exact wording. Every entry is dated with where it came from. Corrections are new entries, never edits. Accountants will recognise this. It's the permanent file, digitised with its discipline intact.

**Stage-keyed context eviction.** Once an extraction table ties out and the user confirms it, the raw document leaves the model's working memory and a stub takes its place. A twelve-month job runs as one continuous session instead of hitting the cliff where the model forgets the first half of the year. No mainstream platform exposes this hook. The minimal harness does.

Underneath those four, two older rules carry over. Arithmetic is never done in the model's head; a separate calculation service does every sum at forty significant digits, and every figure traces back to its inputs. And every finished working paper gets an adversarial cold review by a model that hasn't seen the job, with the findings presented to the partner verbatim.

### What the first full run looked like

The first end-to-end job on this build was a real sole-trader year. The bank tied out to the penny. The cold review produced thirteen findings, including one real figure error, caught before any human had looked at the file. Mechanical legwork was a small fraction of the model spend, which is the delegation rule working. And the manager and worker slots ran different models from the setup examples, swapped by configuration alone, which is the model-agnosticism claim being tested rather than asserted.

That's one run, recorded in the repo, not an audited result or a rollout. I'm careful about that distinction and I'd like other people to be.

### The 80% cap

In July, an earlier build ran head-to-head against the firm's top accounts preparation staff on live jobs. It did about 80% of the work in about a quarter of the time, with the figures matching and a human in the loop throughout.

The 80% is deliberate. After twenty correct outputs in a row, review turns into a reflex, and the twenty-first error goes through. So automation is capped to keep the reviewer doing real work.

What that looks like in practice: the system doesn't run the job to the end and hand over a finished file to be checked. It stops and asks, the way a junior would. A payment it can't place. A figure that doesn't tie out. A policy that reads two ways. A client detail it doesn't have. The person answers, and that answer steers the rest of the job and fixes the output before it's finished rather than after. The 20% held back is that judgement, spread through the work, and it's what keeps the checking honest. I think this is the single most important design decision in the system, and I've written a separate piece on it.

### Where this sits against everything else

There are three kinds of AI product an accountancy firm gets offered right now.

Research tools over a proprietary content library. They answer "what do the rules say". Useful, and a different job. My system does the engagement work itself, with research as one lane of fourteen, answering from live official sources with citations and dates.

Agents inside one accounting platform. They automate inside that platform. Mine is the practice's own front desk across every source a client sends, carrying the firm's own methodology rather than the vendor's.

Generic copilots. Impressive on a one-off document. No enforced method, no firm methodology, no client memory, and no working paper a partner can initial.

The moat isn't the models. Everyone rents the same ones and they improve underneath you. The moat is the enforced working method, the methodology encoded as skills, and the user-approved client memory that stays with the firm. Six months of a staff member's corrections make the system theirs. That investment doesn't transfer to a competitor's product, which is also the retention story.

### The shape, for people who like shapes

If you want the technical framing: the architecture is neurosymbolic in shape. Neural models do the reading and the judgement. Symbolic structures hold everything that must not drift: deterministic arithmetic, the job stage machine, the enforced role denylists, and the domain methodology encoded as charts of accounts and skill files. The plain version is "the model never holds what code can hold better".
