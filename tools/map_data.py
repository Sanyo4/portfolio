"""Content for the full map page (map/index.html).

Every fact here comes from Sanay's KB and LinkedIn copy. Public rules apply:
no client names, no performance or cost figures, no model vendor names
except Microsoft 365 Copilot. Edit here, then run tools/build-case-studies.py.
"""

WORK = [
    {
        "when": "Aug 2025 to now",
        "role": "Automation Project Manager, part-time",
        "org": "Innovi Advisors, a UK accountancy practice",
        "text": [
            "I own the firm's AI programme, from partner discovery through to staff using it.",
            "I interviewed the partners to find where staff time went and worked out why 15 draft agents had stalled. They approved the phased plan I presented. Then I built Oracle, one agent staff brief like a junior: it asks clarifying questions and routes the work, so nobody has to pick a tool. The automation is capped on purpose so a person makes the judgement calls.",
            "I run the staff training, built Alfred, a support agent that points colleagues to the right tool, wrote the firm's whitepaper on AI-assisted accounts preparation and started its AI policy, based on ISO/IEC 42001. Now I'm leading the rebuild of Oracle as a product the firm owns.",
        ],
        "link": ("../case-studies/fifteen-agents-one-front-desk.html", "Case study: Fifteen agents, one front desk"),
    },
    {
        "when": "Aug 2026",
        "role": "AI discovery and adoption, client work through Innovi",
        "org": "A national UK pharmacy group, GPhC-regulated, about £500m turnover",
        "text": [
            "My first client of my own. I ran three discovery days on site with Finance and HR, reporting to the Executive Director.",
            "Three Microsoft 365 Copilot agents shipped in three days, and HR staff built two of them after a one-hour session with me. Then I wrote and sent the discovery letter: what shipped, what it needs to work, and who should own the next phase.",
        ],
        "link": ("../case-studies/ten-things-pharmacy-group.html", "Case study: Ten things I learned"),
    },
    {
        "when": "May to Aug 2024",
        "role": "Builder and facilitator",
        "org": "Treehouse Innovation, London and Cardiff",
        "text": [
            "Project-managed a booth for the Futures Lab at Legal Tech Talk (2,500+ attendees). I built the app that drew visitors' futures of the legal industry, and a tool that digitised the workshop's facilitation cards.",
            "I helped build a workshop on how different personas feel about where the industry is going, and co-authored the published report.",
        ],
        "link": ("https://treehouseinnovation.com/case-studies/the-futures-lab-at-legaltechtalk-2024/", "The Futures Lab report"),
    },
    {
        "when": "Feb to Mar 2024",
        "role": "Digital Automation Insight",
        "org": "Highfield HR, Bridgend",
        "text": [
            "Used design thinking to find the pain points in writing employee contracts, then prototyped a low-cost web app to automate it that the firm could offer its own clients. I also showed the staff how to use AI in their work.",
        ],
    },
    {
        "when": "Jun to Sep 2023",
        "role": "Design coach intern",
        "org": "Treehouse Innovation, London",
        "text": [
            "Designed games and interactive exercises for a 200-person corporate event on a manufacturer's operating model review. I also researched cognitive biases for a gaming company project and built a prototype app for a risk and compliance breakout session.",
        ],
    },
]

LEAD = [
    {
        "when": "2025 to Jul 2026",
        "role": "Head of Events and Outreach",
        "org": "AI Safety Cardiff University",
        "text": [
            "I ran the society's events programme and outreach.",
            "I pitched a guest lecture on AI safety fundamentals to the society's president, then designed and gave it for Cardiff's Emerging Technologies module, to students outside the society.",
            "I also completed its Fundamentals Fellowship: governance and policy readings, and in-session exercises that included making policy decisions during a simulated AI incident.",
        ],
        "link": ("https://aiscu.org", "aiscu.org"),
    },
    {
        "when": "Dec 2024 to Mar 2025",
        "role": "Advanced Design Mentor",
        "org": "STEAMunity, with SUTD and Science Centre Singapore",
        "text": [
            "Mentored six students aged 14 to 20 in design thinking and project-managed the group, working with Metta Cafe on task independence for young people with special needs.",
            "Their plant sensor project, BloomBuddy, won Best Prototype, and they presented it to Deputy Prime Minister Heng Swee Keat.",
        ],
    },
    {
        "when": "Nov 2024 to Sep 2025",
        "role": "Volunteer researcher",
        "org": "ALITA, the Asia-Pacific Legal Innovation and Technology Association",
        "text": [
            "Desk research on legal tech taxonomies for ALITA's Asia-Pacific ecosystem map, and work on the State of Legal Innovation in Asia-Pacific report 2025.",
            "I also helped on site at Lawtech Drinks and Theatre in Singapore and the Asia Pacific European Legal Innovation and Tech Dialogue in London.",
        ],
    },
]

EDUCATION = [
    {
        "when": "2022 to 2026",
        "role": "BSc Computer Science with a Year of Study Abroad",
        "org": "Cardiff University",
        "text": [
            "Graduated in July 2026 with First-Class Honours. I led the Year 2 group project, which gamified internship assessment tasks.",
        ],
    },
    {
        "when": "Sep 2024 to May 2025",
        "role": "Exchange year, Information Systems Technology and Design",
        "org": "Singapore University of Technology and Design (SUTD)",
        "text": [
            "Took the masters-level module Innovation by Design, alongside AI Applications by Design, AI by Design and History of Surveillance in Modern Asia.",
        ],
    },
    {
        "when": "2020 to 2022",
        "role": "A levels: Maths, Physics, Computer Science",
        "org": "Whitgift School, Croydon",
        "text": [
            "My EPQ asked whether we should worry about the misuse of personal data online. Outside lessons it was rowing and theatre.",
        ],
    },
]

WINS = [
    ("Tooling winner", "Jun 2025", "Hack the Law, LLM x Law", "University of Cambridge. Grand finalists too, with a tool that makes dense financial regulation searchable.", "var(--ver)", "-3deg", "14px"),
    ("Golden Glasses", "", "Smart glasses bootcamp, NUS", "Most engaging presentation, for an app on AR glasses that warns travellers about risky areas.", "var(--slate-3)", "2.5deg", "4px"),
    ("1st prize", "", "Design Innovation Day", "MiFutures, run by Fintech Wales.", "var(--sage-4)", "-1.5deg", "26px 6px"),
    ("Finalist", "", "Web3 hackathon", "EasyA, VeChain and BCG. I entered solo.", "var(--ver)", "2deg", "4px"),
    ("First build", "Spring 2026", "Cerebral Valley, Zero to Agent", "A hackathon in London, where I built the first version of Gonzo.", "var(--slate-3)", "-2deg", "14px"),
    ("Only student", "", "TFW and Amey Consulting hackathon", "The one student in a team of industry professionals, building an MVP for TFW 2.0.", "var(--sage-4)", "1.5deg", "26px 6px"),
    ("National B final", "", "Rowing, under-15 coxed four", "We won it. I was the cox.", "var(--slate-3)", "-2.5deg", "4px"),
    ("Lady Macbeth", "", "School theatre, Whitgift", "Also in the first student-led play, Another Country, and scouted by an acting agency at 15.", "var(--ver)", "3deg", "14px"),
]

PRINTS = [
    ("cam-stage", 360, 240, "Me with a microphone presenting at the Hack the Law hackathon in Cambridge, a teammate beside me.", "Hack the Law, Cambridge", "-2deg", " tape"),
    ("glasses", 360, 240, "The smart glasses bootcamp team lined up with our certificate at NUS.", "Golden Glasses, NUS", "-1.5deg", " tape tape--ver"),
    ("web3", 360, 270, "Me and another participant giving a thumbs up at the Web3 hackathon.", "Web3 hackathon, finalist", "2deg", ""),
    ("treehouse", 360, 166, "The Treehouse Innovation team at the Legal Tech Talk booth.", "Treehouse at Legal Tech Talk", "2.5deg", " tape"),
]

MADE = [
    ("https://natter-landing.vercel.app", True, "App · Sep 2026", "Natter", "A voice journal that writes the entry for you, on the phone, with nothing sent anywhere. Beau and Gonzo are folding into it.", "natter-landing.vercel.app ↗"),
    ("../case-studies/beau.html", False, "Built solo · Jan to Feb 2026", "Beau", "A matching app that watches how you react to a social moment instead of asking you to describe yourself. Taken to a working beta with real users.", "Case study →"),
    ("../case-studies/gonzo.html", False, "Hackathon, then solo · Mar to Apr 2026", "Gonzo", "A travel engine that searches in the local language, lets personas argue over the answer, and checks every place against the map.", "Case study →"),
]
