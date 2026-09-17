---
slug: ten-things-pharmacy-group
kind: Case study
title: Ten things I learned putting AI into a national pharmacy group
short_title: Ten things I learned in a pharmacy group
standfirst: Three days of discovery that turned into building. Three agents shipped, four didn't, most of the time went on access, and governance moved from the back of the proposal to the front.
date: August 2026
intro: Notes from three days inside a UK pharmacy group with a few hundred branches, a support office, an offshore back office, and a Microsoft 365 Copilot licence most staff had only ever used as a chat box. August 2026, delivered through the accountancy firm I work for.
---

The brief was a three-day discovery. Two days on site with Finance and HR, one day writing up, and a prioritised backlog with time estimates at the end. On the first morning the Finance team asked for working agents they could see, so they could judge the value before committing to anything wider. Fair enough. Discovery became building.

Three agents shipped in three days, all in Microsoft's own agent builder. One checks expense claims against the written policy and returns a workbook, a summary, and a Q&A over its own output. The other two were built by HR staff themselves after an hour with me. Four more were built for Finance and none of them shipped. Roughly two of the three days went on laptop setup, permissions, a SharePoint access request, and a sync delay on Microsoft's side.

That's the raw material. Here's what it taught me, most important first, then the rest counting down to the one I'd put on a poster.

### 1. Senior people held two different theories of what "value" means

One view: value is the finished output. Build it, show it, and if it works we go wider. Learning how it works is optional. The other: value is capacity. The tool handles the routine work, the person stays in charge, briefs it and checks it. Both views were sincere and both were held by senior people, and nobody had said the difference out loud.

They lead to different programmes. The first produces a few large agents that are hard to get right and easy to distrust. The second produces many small agents that people own themselves. The evidence pointed to the second, and the readout said so plainly so everyone could build towards the same thing.

The first view also creates a loop. You need the output to see the value, but a good output needs criteria first. The loop is breakable; the expense checker broke it, because it had a written policy behind it and a small scope. It just has to be broken on purpose, every time.

### 2. Accountability and authority have to sit together

Whoever builds and runs an agent carries the blame when its output is wrong and gets acted on. That's fair. It's also why the role needs authority to match. Over the three days, scope and priority were set by the requesting team in the room and changed several times, while responsibility for the result sat with me. Fine for a first week. As a standing arrangement in a regulated business, it's a person absorbing risk they can't control.

The daily ops role a business like this needs is a real one. But the spec has to give it a reporting line to the sponsor, a say on what gets built and how, the right to send an unready request back, a desk with the teams, and a level that matches the risk. Filling it cheaply is the expensive option.

### 3. Teaching beat building

Three days of building for Finance shipped nothing. One afternoon of teaching HR shipped two agents, built by HR. The expense checker shipped the same afternoon, once it was rebuilt small with the sponsor in the room.

Every agent that shipped came from the same method: one sitting, one small task, the person who does the job present to say whether the output was right. Every agent that didn't ship was built over days for a team still deciding what it wanted. Same builder, same three days. The method decided the result.

### 10. Where you sit decides what you find

Every good idea I've had in this kind of work came from sitting next to someone until they said "I hate doing this bit". The client laptop only worked in a meeting pod, so I spent most of three days apart from the teams. The discovery method got disabled by a device policy. A desk with the team, with access cleared in advance, now goes in the engagement letter.

### 9. The brief changes on contact

The discovery was agreed with the Executive Director. The people in the room on day one hadn't been part of that conversation and, reasonably, asked for what they wanted: working agents, now. Twenty minutes of "what this is, what it isn't, and what we'll have by Wednesday" with the room before any building would have saved a day. Set expectations with the people in the room as well as the sponsor.

### 8. Some access questions are policy decisions nobody has been asked to make

One connector request, for a free, read-only integration already covered by an existing licence and inside the existing governance, was still not cleared when the laptop went back. That's less a queue problem than an open question: is it permitted or not? Nobody had been asked to decide. An approved tools register, where those decisions get made and written down, is what stops the next request waiting three days for an answer that doesn't exist yet.

### 7. Access time is the real rate limiter

The people were willing. The tools were adequate. What set the pace was how long it took to get a laptop that charged, a licence that showed up, a folder that synced, and a connector approved. AI work needs access on day one, and most IT processes were built for a slower cadence. There's a nasty side effect too: when the tool has already been ruled out as the cause ("Copilot isn't the problem"), every unexplained delay lands on the person delivering. An access checklist, cleared before day one, belongs in the plan before any building starts.

### 6. Task shape decides the agent, not the vendor

Expense compliance has a written policy behind it. "Correct" exists on paper, so the agent can be tested against it and trusted quickly. Cash flow has no single right answer; the agent drafts, a person decides. Sort the backlog by shape before you sort it by value.

The same sorting applies to size. The Copilot builder is good for email-shaped, checklist-shaped and lookup-shaped work. Long reasoning over a folder of seventy large PDFs breaks it, and that's true of every small model behind every chat product. A Gemini Gem, a Claude project and a Copilot agent are the same object (a description, some instructions, some knowledge files), so the real differences are the model and the context limit. The design rule is one narrow agent per task, with curated knowledge rather than a whole library.

### 5. The tool won't tell you it can't

Ask an agent for something beyond it and it builds something that looks similar. It never says no, and the person who asked reads the output as what they asked for. Nothing in the builder catches the gap. So the buyer becomes a co-author whether they like it or not, and the only reliable check is a written description of a correct output plus a named reviewer.

One Finance agent was rebuilt several times because it was being judged against a picture that had never been written down. That's not a criticism of anyone. It's how the tools behave.

### 4. Governance is the product, not the caveat

An agent register (owner, reviewer, written criteria, data sources). A rule that agents draft and people send. An approved tools register. A one-page standard for how to build an agent. Short red-flag training. Proportionate to the business, built on ISO/IEC 42001 principles.

I used to present that list as the responsible-adult section at the end of a proposal. Three days here moved it to the front. It isn't the brake. It's what lets Finance get the outputs they asked for, what stops the tools being a black box one person owns, and what makes the role in insight 2 survivable. In a regulated business, the fastest way to kill an AI programme is to auto-send something wrong in month one.

### What I recommended

Microsoft's Copilot suite as the platform, used as a ladder rather than one product. Copilot chat for everyday work, which most staff hadn't started on. The in-Copilot agent builder for small personal agents: all three shipped agents live there, and it's where a team should build its first one. Copilot Studio for the agents that need to be shared, connected or audited, because it adds the connectors, actions, publishing and audit trail the basic builder lacks. Already licensed, data inside the tenancy, their IT can support it. I'd have picked something else for myself. The decision was already made, and my credibility was better spent on scope and oversight.

Then the governance layer above before any more Finance builds, phase two built the way the three shipped agents were built, and a daily ops role specified with the authority to hold that line.

### Why this isn't a pharmacy story

The pattern isn't specific to pharmacy. A licensed AI tool most staff don't use. A senior team that wants proof before investment. An IT function whose approval loop is slower than AI work needs. A disagreement about what "value" means that nobody has said out loud. And a role that carries the accountability without the authority. If you're about to walk into a business with that shape, the ten above are what I'd want to know on day one.
