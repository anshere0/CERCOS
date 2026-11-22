# TEAM — CERCOS (EPICS Phase-I)

Six peers, one repository, one shared goal: **40% of CERCOS delivered, working, reviewed and explainable by every member.**

## Roster, areas and share of the 40%

| Member | Area owned | Phases | Share | Personal guide |
|---|---|---|---|---|
| **Ansh** | Repository, infrastructure, CI, database migration, integration tests | P0, P4 e2e | 6 | `docs/team/ansh.md` |
| **Atharva** | Recommendation engine, queue model, simulation | P2, P3 analysis | 8 | `docs/team/atharva.md` |
| **Yash** | Data pipelines, database models, backend API | P1, P4 API | 8 | `docs/team/yash.md` |
| **Anshuman** | Frontend: map app, Field Mode forms | P4 UI, P3 forms | 7 | `docs/team/anshuman.md` |
| **Kashish** | Field research: census, survey, queue observation, BWM analysis | P3 | 6 | `docs/team/kashish.md` |
| **Eshwari** | Literature, policy and Vahan data, corridor spacing, Phase-I report | P1 data, Report | 5 | `docs/team/eshwari.md` |

Total = 6 + 8 + 8 + 7 + 6 + 5 = **40**. Shares measure the amount of project work, not importance. Every area is required: without field data there is no research, without the engine there is no recommendation, without the report there is no submission.

## How we work as equals
- **Areas are ownership, not rank.** Nobody reports to anybody. Each person decides how to build their own area and answers for it.
- **Every change is reviewed by a peer.** No one merges their own pull request. The reviewer merges after approving.
- **Everyone has the same powers:** open issues, request changes, block a merge that fails the checklist, call a vote.
- **Decisions:** technical choices inside an area belong to its owner after hearing objections. Cross-area decisions (contracts, schema, scoring rules, scope) need a vote at the Monday meeting: 4 of 6 carries. A 3-3 tie goes to the faculty supervisor.
- **Meeting facilitator rotates weekly:** W1 Ansh, W2 Atharva, W3 Yash, W4 Anshuman, W5 Kashish, W6 Eshwari, W7 Ansh.
- **Admin rights on GitHub** are used only for setup. The branch ruleset binds every account, including the repository owner's.

## Review pairs (who reviews whom)

| Author | Primary reviewer | Secondary reviewer |
|---|---|---|
| Ansh | Atharva | Yash |
| Atharva | Yash | Ansh |
| Yash | Anshuman | Atharva |
| Anshuman | Ansh | Yash |
| Kashish | Eshwari | Atharva (analysis scripts) |
| Eshwari | Kashish | Ansh |

The primary reviewer must respond within **24 hours**. If they do not, the secondary reviewer takes over.

## Field visits (all six take part, in pairs)
Faculty accompany or approve every visit. Pairs rotate so everyone sees both the city and the corridors.

| Zone | Pair A | Pair B | Pair C |
|---|---|---|---|
| Bhopal city | Kashish + Anshuman | Eshwari + Yash | Atharva + Ansh |
| Bhopal–Sehore–Ashta | Eshwari + Yash | Atharva + Ansh | Kashish + Anshuman |
| Bhopal–Vidisha–Sanchi | Atharva + Ansh | Kashish + Anshuman | Eshwari + Yash |
| Bhopal–Narmadapuram–Raisen | Kashish + Anshuman | Eshwari + Yash | Atharva + Ansh |

Pairs split the zones between them. Kashish keeps the master schedule, but each pair is responsible for completing its own visits.

## Everyone's non-negotiables
1. **6 hours per week minimum**, logged in the paper record book **and** in `docs/team/logs/<yourname>.md`.
2. **Understand what you commit.** AI-generated code counts only if you can explain it at the viva.
3. **Stay in your folders.** Need a change elsewhere? Open an issue for that owner.
4. **Never commit** secrets, raw survey data or photos of people.
5. **Never present synthetic results as real.** Label them `synthetic` everywhere.
6. **Never leave anyone blocked.** Post blockers in the group chat within 24 hours.
