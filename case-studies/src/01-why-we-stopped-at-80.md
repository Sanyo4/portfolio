---
slug: why-we-stopped-at-80
kind: Essay
title: Why we stopped at 80%
standfirst: The AI did about 80% of the work in about a quarter of the time. Why we chose not to push it to 100, and the handful of things I now believe about putting AI into real work.
date: August 2026
start_here: true
---

Earlier this year the AI system I'd built for an accountancy firm went head-to-head with the firm's best accounts preparation people on live jobs. It did about 80% of the work in about a quarter of the time. The figures were right.

The number people ask about is the 80. Why not 100? We could probably have pushed it higher, and we chose not to. This post is about that choice, and about the handful of things I now believe about putting AI into real work, most of which I learned by getting them wrong first.

### Review at the end doesn't scale

Picture a reviewer checking AI output. The first output is wrong in a small way and they catch it. The next twenty are right. What happens on the twenty-second?

They wave it through. Not because they're lazy. Because twenty correct outputs in a row have turned review into a reflex, and a reflex doesn't read. Oversight degrades precisely when the automation gets good. That's the trap, and "we have a human in the loop" doesn't get you out of it if the human is a rubber stamp at the end of a finished file.

So we capped the automation. The system does the reading, the extraction, the sums, the drafting. It leaves the person a real piece of work to do: the judgement calls and the client knowledge. Is that four grand a month rent, or the director repaying a loan? If the reviewer is doing something that needs their brain, they're awake for the rest of it.

The 20% held back isn't a shortfall. It's the safety mechanism.

### The human belongs in the middle, not at the end

The cheaper version of the same idea: the moment to ask a person is when the ambiguity first appears, before a wrong assumption propagates through everything downstream.

The way I say it out loud now is that the system should ask questions the way a good junior would. A junior who hits something they don't understand on day two doesn't build a whole set of accounts on a guess and hand it over on day ten. They come and ask. The human stays in the loop on nuance and judgement, answering what a junior would come and ask, rather than signing off a finished file they haven't really read.

### Accountability can't be delegated to software

In regulated professions the rules say so. A machine can't carry the responsibility for an engagement. A person signs and a person answers for it. Everywhere else, it's what makes the output worth trusting.

This has a sharp edge I only saw properly this month, working with a pharmacy group. Whoever builds and runs an agent carries the blame when its output is wrong and someone acts on it. Fine. But then that person needs the authority to match: a say on scope, the right to send an unready request back, a reporting line to the sponsor. A role that has the accountability without the authority is a person absorbing risk they can't control. If you're specifying that role, write the authority in before you hire.

### An agent won't tell you it can't

Ask one of these tools for something beyond it and it builds something that looks similar. It never says no. So the buyer becomes a co-author whether they like it or not.

The only reliable defence is a written description of what a correct output looks like, and a named reviewer who owns that description. I watched an agent get rebuilt four times because it was being judged against a picture in someone's head that had never been written down. That isn't a criticism of the person. It's how the tools behave. Governance isn't the brake on this work. It's what makes the output people actually want possible.

### Task shape decides the agent

Some work has a written rule behind it. Expense compliance against a policy. VAT boxes against HMRC guidance. "Correct" exists on paper, so the agent can be tested against it and trusted quickly. Automate that hard.

Some work has no single right answer. A cash flow forecast. A judgement on whether a client relationship is a going concern. The agent drafts, a person decides, and pretending otherwise is how trust gets lost.

Sort the backlog by shape before you sort it by value. Most of the arguments I've seen about "does AI work for this" were really arguments between people who had different task shapes in mind.

### Rules that matter go in code

A rule the software can break under load is a suggestion, and the telemetry shows it eventually breaks. "Please delegate the cheap work to the cheap model" held until it didn't. "Don't send without review" holds until the day someone's in a hurry.

So the rules that matter get enforced by the system. The expensive model doesn't have the tool to read source documents, so it has to delegate. Arithmetic runs in code, because a wrong sum from a model looks identical to a right one. The email is drafted, never sent. If a rule is important, don't ask the model to follow it. Make it structurally impossible not to.

### The system should learn you, and you should own that

When the system asks about the four grand from J. Smith and you say "that's the director's loan", it offers to write that down. You approve the wording. It's saved with the date and where it came from. Next quarter, it doesn't ask.

Six months in, the system is good because of the corrections you fed it. That training is yours and your firm's. It doesn't belong to the software company and it can't be downloaded by a competitor. This is the opposite of being made interchangeable. You become the one person your system works best for.

### Models are commodities

The models improve underneath the product and swap by configuration. On the latest build, the manager and worker slots ran different models from the ones in the setup docs, and the change was a config file. The durable value is the enforced working method, the encoded methodology, and the accumulated approved memory. Anyone who tells you their moat is the model is renting their moat.

### You're not being replaced, you're being promoted

I gave a talk to the staff with that title, because the 80% number sounds like a threat until you look at what's in the 80.

The 80% is the reading. Opening twelve bank statements. Typing out hundreds of transactions. Adding them up. Nobody gets their professional letters for being fast at that. The 20% is knowing the client, spotting what's odd, and the signature. That was always the actual job. It just spent years buried under data entry.

Every generation of this profession has had a version of this moment. Calculators were going to replace accountants, and then spreadsheets were. Each time the mechanical part shrank and the advisory part grew. This is the same moment, just bigger. The new junior starts whenever you're ready to start training it. And never, ever rubber-stamp it.
