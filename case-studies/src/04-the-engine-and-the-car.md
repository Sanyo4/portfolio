---
slug: the-engine-and-the-car
kind: Case study
title: "The engine and the car: why I moved our AI system three times in one summer"
short_title: The engine and the car
standfirst: The same system ran on three different harnesses between June and August. Same skills, same integrations, same rules. Where the value actually sits when the model is a line in a config file.
date: August 2026
---

The system I build for an accountancy firm has run on three different harnesses since June. Same skills, same integrations, same rules. Three engines under the same bonnet. This is why, and what it taught me about where the value in one of these systems actually sits.

### Engine, car, driver

The analogy I use with the partners: the model is the engine. The harness is the car. The harness is everything around the model that turns it into a system you can hand to an accountant: which tools it can reach, how it hands work to subagents, what it remembers, what it forgets, when it stops and asks a person.

Most of the industry sells you the engine and the car as one thing. You rent a platform, the model is bolted in, and the rules you care about are prompts you write and hope it follows. That's fine to start. It's what we did.

### Harness one: rented

The first production build ran on a commercial platform. The router and forty-odd specialist skills were markdown. The integrations were standard connectors. It worked, it was benchmarked against the firm's best staff in July, and it's still in production today.

Two things bothered me even while it was working. The rules that mattered were requests, not guarantees. "Delegate the mechanical work to the cheap model" held until it didn't, and when it stopped holding, the expensive model was quietly doing extraction at about eleven times the input price. And the per-seat pricing looked subsidised to me, in a way I'd expect to move to usage-based once the market settles. Building the firm's whole method on top of someone else's pricing decision felt like a bet I didn't want to make on their behalf.

So I'd built the first version to be portable on purpose. Skills as markdown, integrations as MCP servers in their own repo, nothing that only worked on one platform. The bet was that we'd want to move the car later without rebuilding the driver's seat.

### Harness two: forked

In late July we collected that bet. Vedas is the same system rebuilt as a product the firm owns: a self-hosted open-source agent engine behind a custom web shell, the skills forked in, the same integrations, deployed in an EU region behind the firm's own sign-in.

The big change wasn't the model. It was metering. Every model call goes through a self-hosted gateway with per-person keys, spend caps, and two abstract slots, "big" and "small", resolved to whatever model we choose that week. The user picks nothing, ever. The model behind a slot swaps in a config file. A deployment for another firm could set its own usage pricing instead of reselling seats.

The first end-to-end production job ran on that build in early August. One request, clarifying questions, fifteen documents pulled from the firm's document system, computed figures, a filed deliverable pack, a person answering questions and signing off throughout.

It also ran into the same wall as harness one, just in a different place. The engine I'd forked could still only ask the model to follow the rules. When a reference was wrong, cheap work silently ran on the expensive model and nothing in any log said so. And the hook I most wanted, evicting a document from the model's working memory once its figures were confirmed, didn't exist.

### Harness three: owned

So in August the whole thing moved again, onto a minimal open-source harness where the rules are code the harness runs rather than text the model reads. The manager model doesn't have the tool to open source documents, so delegation is structural. Workers return a fixed contract and their transcripts are thrown away. Model slots are validated loudly at startup. Memory writes need the user to approve the exact wording. And once an extraction table ties out, the raw document leaves the model's context and a stub takes its place, so a year-long job runs as one session.

That took days rather than weeks, because the skills and the integrations moved unchanged. The first full job on it was a real sole-trader year with a bank tie-out to the penny and a cold review that caught a real figure error before a human saw it. In the same run, the manager and worker slots ran different models from the ones in the setup docs. The swap was configuration.

Three harnesses. The skills, the methodology and the integrations never changed. That's the point.

### The engine doesn't need to be the biggest one

Here's the part people don't expect. For the work an accountancy practice actually does, a mid-tier frontier model is plenty. In my experience a Sonnet-class model handles the router, the categorisation and the judgement calls perfectly well. The frontier model isn't the bottleneck. Access, data structure and written criteria are, every time.

And as far as I can tell, the open-weight models have caught up for this class of work. A 27-billion-parameter model you can run on a single machine now matches the mid-tier rented ones on the jobs I care about. I haven't benchmarked that to a standard I'd publish; it's the working read from running them.

That changes the economics in two ways. First, cost: if the manager slot can be a mid-tier model and the worker slot can be a small open-weight one, the model spend on a whole job is small enough that the pricing question becomes about the method, not the tokens. Second, where it runs: open-weight models on a carbon-neutral data centre, or inside the firm's own boundary, are a real option for a regulated business that would rather not send client documents to a vendor at all. The harness doesn't care. The slot resolves to whatever's behind it.

### What this means if you're building one

The value in a system like this isn't the model. Everyone rents the same ones, they improve underneath you, and they swap. The value is three things the model can't hold: the enforced working method, the methodology encoded as skills, and the user-approved memory that makes the system theirs. Own those, in a form that survives a harness swap, and the engine becomes a line in a config file.

Rent the harness to start. It gets you to a benchmark faster than anything else. But build as if you'll leave, because you will, and because the rules that keep a regulated firm safe shouldn't depend on a model agreeing to follow them.
