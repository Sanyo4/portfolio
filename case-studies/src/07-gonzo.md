---
slug: gonzo
kind: Case study
title: "Gonzo: six personas, one argument, and a phone call to Google Maps"
short_title: Gonzo
standfirst: A travel engine that searches in the local language, lets six personas argue over the answer, and checks every place against Google Maps before it's allowed to recommend it.
date: August 2026
link_label: gonzo.guide
link_url: https://gonzo.guide
---

Gonzo started at a hackathon in London in spring, run by Google DeepMind and Vercel, and I kept building it for a couple of months afterwards. It's a travel recommendation engine that finds the places guidebooks don't know about. The app is shelved. The idea underneath it is the one I use most.

### The problem with "best restaurants in Prague"

Every travel recommendation product gives you the same fifteen places, because they all search the same English-language listicles. The stuff worth finding is on a Czech forum, argued over by people who live there, and it's a pub that doesn't have a website.

Gonzo's first move is to search in the local language. The model works out a city's primary language and searches in that, so the query is "nejlepší hospoda Praha" and not "best pub Prague". You get what locals actually discuss.

Its second move is a personality. You pick a lens. Local, who wants the place with no sign. Plot Twist, who wants the night to go somewhere odd. Foodie. Hangover, who needs grease and a dark room. Bougie. Budget. Each one sees the same city completely differently and surfaces different places.

### Council mode

The bit I'm proudest of. Pick two or three personas and they argue.

The cheap way to do this is one model pretending to be three people in one reply, and it's rubbish, because a single model roleplaying an argument always converges on a polite compromise. Gonzo does it properly. Each persona runs its own search in parallel. Then they debate in character across several sequential turns, each seeing what the others argued last round. A final synthesis call picks a winner and says why.

This is an orchestration pattern dressed up as a game. I wanted to know how multi-agent debate behaves when the agents are actually separate, and the answer is: better, but you pay for it in calls, so you need a reason.

### Nothing gets recommended unless it exists

Language models make up restaurants. Confidently, with an address. So every candidate Gonzo finds goes through a second check against Google Maps: does this place exist, and is it open right now? If it's closed, it's demoted and the search goes again. Nothing reaches the user that hasn't been verified against a live source.

It also reads the weather. Rain gets you indoor picks. Clear skies get you a rooftop.

And it burns what it shows you. Only the winning recommendations are saved per persona, city and user. Ask again and it has to go deeper rather than recycling the same picks. Repeated queries get weirder, which is the point.

### The build

A web app plus a Telegram bot plus a Discord bot, all tied to one identity through a magic-link email login. A small, fast model with search grounding to find candidates, Maps grounding to validate, structured parsing between the two. Pricing was a free tier with the Local lens only and a cheap monthly plan for all six personas and council mode.

The whole pipeline was designed to keep model calls low: one search call, one parse, one Maps check, retry only on failure. Council mode adds the parallel searches and the debate turns, and that's the one feature where the cost was allowed to go up because it was the feature.

### What carried over

Two things went straight into my work building agents for firms.

The verification layer. "The model says X, now check X against a source that can't hallucinate" is the same shape whether the source is Google Maps or a company's own written policy. Gonzo taught me to build that check in as a stage, not a hope.

The orchestration discipline. Council mode is a small version of a manager model briefing separate workers and synthesising what comes back. The difference between one model pretending to be a team and an actual team of calls is a lesson I've since had to relearn at a much larger scale, in code, with money on it.

### Where it is now

The app is shelved. I might rebuild it. The persona, though, never stopped. Gonzo lives on as the brain I use to plan my own trips and nights out: a persona brief, a taste profile, a scoring method with three axes, and a growing list of field lessons from places that were and weren't worth it. Any AI I plan travel with loads that first. The product went quiet. The point of it didn't.
