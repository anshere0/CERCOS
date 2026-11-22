# ANSHUMAN — Frontend: Map App & Field Mode  (7% of the 40%)

**Mission:** a clear, fast, mobile-friendly interface that (1) lets a driver get a recommendation and see why it was chosen, and (2) lets the team record census, survey and queue data in the field. You turn everyone's work into something people can use and the faculty can see.
Your PRs are reviewed by **Ansh** (primary) and **Yash** (secondary). You review **Yash** (primary, as the API consumer) and **Kashish's** field-form flows when asked.

## You own
`frontend/` (everything inside) · `docs/UI.md`

## Inputs / Outputs
| You need | From | When |
|---|---|---|
| `contracts/openapi.draft.yaml` (build against mocks) | already in repo | now |
| Final field instruments (fields, wording, 9 BWM comparisons, consent text) | Kashish | W1 (by 27 Nov) |
| Live API | Yash | 20 Dec |
| Explanation fields | Atharva (contract) | now |
| **You deliver** | | |
| Field Mode forms | Kashish, Eshwari | **6 Dec** (Google Forms cover fieldwork until then) |
| Recommend UI + comparison panel | everyone | 20–27 Dec |
| Demo recording and `docs/UI.md` | Eshwari, Ansh | 10 Jan |

## Task list by week
**W1:** Vite + React + TypeScript + ESLint scaffold; MapLibre or Leaflet on OpenStreetMap tiles centred on Bhopal; typed API client generated from the draft OpenAPI; mock server (MSW or JSON fixtures) so you never wait for the backend.
**W2:** Field Mode (mobile first, installable PWA): **Census form** (GPS capture, photo of equipment only, validation); **Survey form** (consent checkbox that blocks submission; segment; **Best-Worst**: choose best and worst of six criteria, then rate the others 1–9 against each = 9 comparisons); **Queue sheet** (slot, vehicles waiting, connectors busy, session start/end). Unsent records stay in the browser queue and sync when online.
**W3:** connect forms to `/v1/field/*`; CSV export page.
**W4:** Recommend page: origin, destination, vehicle, SoC, mode; result cards (score, cost, wait, arrival SoC, "why this one"), route and station markers.
**W5:** **Nearest vs CERCOS comparison panel**; station detail drawer (all fields from the spec: name, location, operator, connectors, speed, cost, rating, hours, contact); provenance badges (`Simulated`, `OSM`, `Census`) and a confidence indicator.
**W6:** responsive layout checked on phone widths; keyboard and contrast accessibility pass; component tests.
**W7:** demo screenshots and a short screen recording; `docs/UI.md`.

## Commit trajectory
| Branch | Commits | PR title | Reviewer | Due |
|---|---|---|---|---|
| `feat/ui-scaffold` | `feat(ui): scaffold vite react typescript` → `feat(ui): base map centred on bhopal` → `feat(ui): typed api client and mocks` | UI scaffold + mocks | Ansh | 29 Nov |
| `feat/ui-field-census` | `feat(ui): census form with gps and validation` → `feat(ui): offline queue and sync` | Census form | Ansh | 4 Dec |
| `feat/ui-field-survey-queue` | `feat(ui): survey form with consent gate` → `feat(ui): best-worst comparison component` → `feat(ui): queue observation sheet` | Survey + queue forms | Ansh | 6 Dec |
| `feat/ui-field-api` | `feat(ui): connect field forms to api` → `feat(ui): csv export page` | Field forms connected | Ansh | 13 Dec |
| `feat/ui-recommend` | `feat(ui): recommend form` → `feat(ui): result cards with explanations` → `feat(ui): route and markers` | Recommend page | Ansh | 20 Dec |
| `feat/ui-compare-detail` | `feat(ui): nearest vs cercos panel` → `feat(ui): station detail drawer` → `feat(ui): provenance badges` | Comparison + details | Ansh | 27 Dec |
| `test/ui-polish` | `feat(ui): responsive layout` → `fix(ui): accessibility issues` → `test(ui): component tests` | Responsive + tests | Ansh | 3 Jan |
| `docs/ui` | `docs(ui): screenshots and ui guide` | UI docs + demo | Ansh | 10 Jan |

## Definition of Done
- `npm run build` and `npm run lint` pass in CI.
- All three field forms work on a phone viewport (≤ 400 px wide), validate input, work offline, and sync.
- The survey **cannot be submitted without consent**, and the app collects no names or phone numbers.
- A user can request a recommendation, see the top 3 with an explanation, and compare against the nearest charger.
- Every station shown has a visible source badge; simulated data is labelled **Simulated**.
- A 1–2 minute screen recording of the full flow exists.

## Antigravity prompt (Planning mode, branch `feat/ui-field-survey-queue`, adapt per task)
```
Read AGENTS.md, contracts/openapi.draft.yaml, docs/FIELD_FORMS.md and prompts/P3_field_tools.md.
You work for Anshuman. Edit ONLY frontend/ and docs/UI.md.
Task: build mobile-first Field Mode pages in React + TypeScript: (1) an anonymous survey with a consent checkbox that blocks submission and a Best-Worst task (pick best and worst of six criteria: detour, cost, wait, speed, rating, battery safety; then rate the others 1-9 against each = 9 comparisons); (2) a queue observation sheet. Validate inputs, keep unsent records in a local queue and sync when online. No names or phone numbers anywhere.
Use the mock API from contracts/openapi.draft.yaml. Plan first. Write component tests. Small commits as in docs/team/anshuman.md. Do not edit other folders. Do not push to main.
```

## Report evidence (your half page)
UI design decisions, the field-mode offline approach, screenshots of the main flows, accessibility notes — with links to merged PRs and the recording.
