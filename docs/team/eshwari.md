# ESHWARI — Literature, Policy & Vahan Data, Corridor Gaps, Phase-I Report  (5% of the 40%)

**Mission:** supply the evidence base (literature, official data, policy norms), produce the first corridor-gap finding (RQ3), and assemble the Phase-I report in the required format. You turn the team's work into the document the faculty grade.
Your PRs are reviewed by **Kashish** (primary) and **Ansh** (secondary). You review **Kashish** (primary).

## You own
`docs/` (except `docs/team/`, `PHASE_REPORT.md` and docs owned by others) · `docs/LITERATURE.md` · `docs/references.bib` · `docs/DATA_SOURCES.md` (first draft) · `data/vahan/` · `data/policy/` · `analysis/corridor_spacing_v0.py` · the Phase-I report file

## Inputs / Outputs
| You need | From | When |
|---|---|---|
| Census station coordinates | Kashish (or OSM/OCM via Yash) | 14 Dec |
| Results and figures | Atharva, Kashish, Yash, Anshuman | W6–W7 |
| Half-page contributions | all five others | W6 |
| **You deliver** | | |
| Vahan CSVs, district boundaries | Yash | 6–13 Dec |
| Literature review (2–5 pages, ≥ 30 references) | whole team | 13 Dec |
| Corridor spacing result | Atharva, Kashish | 20 Dec |
| Report skeleton, then final report | whole team | 27 Dec / **10 Jan** |

## Task list by week
**W1:** reading list and comparison table (rows: paper; columns: method, vehicles covered, criteria, data, what it misses). Build `docs/references.bib` with **verified** entries only. Open every paper's publisher page; verify volume, pages and DOI. Start from the candidates in the dossier and drop any you cannot verify.
**W2:** `docs/DATA_SOURCES.md`: exact **Vahan dashboard export steps** (district × vehicle class × fuel, state MP, years), licence notes, and how each file was obtained. Collect CSVs into `data/vahan/`. No scraping.
**W3:** MP district boundaries (GeoJSON, with licence note) into `data/policy/` or `data/vahan/` as agreed with Yash; policy summary: MoP/BEE guidelines (3×3 km, 25 km, 100 km), MP EV Policy 2025, the Ministry of Heavy Industries reply of 27 Mar 2026 (cite its table: MP 1,417 installed, 1,291 operational on 1 Mar 2026). Literature review draft with the gap statement.
**W4:** corridor polylines (OSM exports for the NH-46 stretch towards Ashta, Bhopal–Narmadapuram, Bhopal–Vidisha–Sanchi) and `analysis/corridor_spacing_v0.py`: snap stations to the corridor, list spacing, flag **> 25 km** and fast-charger **> 100 km** gaps; CSV and chart.
**W5:** report skeleton following the Phase-I format: Times New Roman 12, single spacing, headings 14 pt, page numbers, figure captions below, table captions above; Introduction (1 page), Motivation (1), Objective (1), Literature (2–5), Topic of the work (10–15), Contributions (≥ ½ page per member), Conclusion (1), References (≥ 30), biodata (½ page per member).
**W6:** figure and table numbering; collect each member's half page; check every claim against its source.
**W7:** assemble, proofread, reference check, plagiarism check, declaration page signed by all, Bonafide page as in the template; submit the soft copy via the Google Form link; confirm the printed Bonafide went to Dr Ashok Kumar Patel.

## Commit trajectory
| Branch | Commits | PR title | Reviewer | Due |
|---|---|---|---|---|
| `docs/literature-start` | `docs(report): add reading list and comparison table` → `docs(report): add verified references.bib` | Literature start | Kashish | 29 Nov |
| `docs/data-sources` | `docs(data): add vahan export steps` → `data(vahan): add district ev csv exports` | Data sources + Vahan | Kashish | 6 Dec |
| `data/districts-policy` | `data(policy): add district boundaries with licence note` → `docs(report): policy summary` | Districts + policy | Kashish | 13 Dec |
| `docs/literature-review` | `docs(report): literature review draft` → `docs(report): gap statement` | Literature review | Kashish | 13 Dec |
| `feat/corridor-spacing-v0` | `feat(analysis): corridor spacing script` → `test(analysis): spacing fixtures` → `docs(analysis): first gap results` | Corridor spacing v0 | Kashish + Yash | 20 Dec |
| `docs/report-skeleton` | `docs(report): add Phase-I report skeleton` | Report skeleton | Kashish | 27 Dec |
| `docs/report-figures` | `docs(report): figures and tables` → `docs(report): contributions section` | Figures + contributions | Kashish | 3 Jan |
| `docs/report-final` | `docs(report): final assembly` → `docs(report): reference check` | Final report | Kashish + Ansh | 10 Jan |

## Definition of Done
- `references.bib` has ≥ 30 entries; each was opened and checked on the publisher or official site.
- Every number in the report has a source in `docs/DATA_SOURCES.md`.
- Vahan files and boundaries exist with licence notes and are loadable by Yash's loaders.
- `corridor_spacing_v0.py` flags every segment over 25 km in test fixtures and produces a CSV and a chart for the real census.
- The report follows the format page for page, includes six individual contributions, and is submitted via the form; the printed Bonafide is delivered.

## Antigravity prompt (Planning mode, branch `feat/corridor-spacing-v0`)
```
Read AGENTS.md, docs/DATA_SOURCES.md and contracts/schema.sql (charging_stations).
You work for Eshwari. Edit ONLY docs/ (not docs/team/), data/vahan/, data/policy/, analysis/corridor_spacing_v0.py.
Task: write analysis/corridor_spacing_v0.py using geopandas/shapely: read a corridor polyline (GeoJSON) and a stations CSV (lat, lon, max_power_kw), snap stations within 2 km of the corridor, project to distance along the corridor, sort, compute the gap between consecutive stations, flag gaps > 25 km (MoP norm) and stretches > 100 km with no station of >= 25 kW. Output a CSV and a PNG chart. Add pytest fixtures with a synthetic corridor (label it synthetic).
Plan first. Small commits as in docs/team/eshwari.md. Do not edit other folders. Do not push to main.
```

## Rules specific to you
- **Cite only what you opened.** An unverified reference gets removed, not "fixed from memory".
- Report text states clearly what is real field data and what is simulated.
- Use the supplied Phase-I template and keep its Bonafide and Declaration pages exactly as given.

## Report evidence (your half page)
Literature method and gap, data sources and licences, corridor-gap method and first result, report assembly — with links to merged PRs.
