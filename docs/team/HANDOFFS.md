# HANDOFFS — who gives what to whom, and by when

A handoff is **complete only when the artifact is merged into `main`** and the receiver has confirmed it in the group chat. Until a real artifact exists, the receiver works against the contract or a mock and never waits idle.

| # | From | To | Artifact | Path | Due |
|---|---|---|---|---|---|
| 1 | Ansh | All | Repo, CI, compose, Makefile, tag `v0.1-foundation` | repo root | 29 Nov |
| 2 | Ansh | Yash | Alembic migration 0001 | `db/` | 28 Nov |
| 3 | Kashish | Anshuman | Final field instruments and consent text | `docs/FIELD_FORMS.md`, `docs/ETHICS.md` | 27 Nov |
| 4 | Eshwari | Yash | Vahan district CSVs | `data/vahan/` | 6 Dec |
| 5 | Eshwari | Yash | District boundaries (GeoJSON) | `data/policy/` | 13 Dec |
| 6 | Kashish | Yash | Census CSV format, then batch 1 | `data/field/processed/` | 13 Dec |
| 7 | Atharva | Yash | `recommend()` function | `backend/app/mcdm/` | 20 Dec |
| 8 | Yash | Anshuman | Live read and field endpoints | API | 20 Dec |
| 9 | Yash | Eshwari | Stations export for the corridor script | CSV from API/DB | 14 Dec |
| 10 | Yash | Anshuman | `/v1/recommend` | API | 27 Dec |
| 11 | Kashish | Atharva | BWM weights, queue statistics, census values | `data/field/processed/`, `analysis/` | 3 Jan |
| 12 | Atharva | Eshwari | Simulation results and `ENGINE.md` | `research/`, `docs/` | 10 Jan |
| 13 | Eshwari | All | Report skeleton and contribution template | `docs/` | 27 Dec |
| 14 | Everyone | Eshwari | Half-page contribution each | `docs/team/` or the report | 3 Jan |
| 15 | Ansh | Eshwari | Final demo build, tags, `PHASE_REPORT.md` | tags, `docs/` | 10 Jan |

**If a handoff is late:** the giver posts a new date and the reason in the group chat the same day. The receiver keeps working against mocks or contracts and the Monday meeting re-plans.
