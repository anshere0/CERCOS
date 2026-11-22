# COMMIT PLAN — the trajectory of `main`

Detailed per-person branch and commit tables are in each person's guide. This page is the overview.
Dates assume Week 1 = Monday 23 Nov 2026. Move them if the review date differs, and update `scripts/issues.tsv`.

## Milestones and tags
| Tag / milestone | Date | Content on `main` | Share reached |
|---|---|---|---|
| Bonafide delivered | by **30 Nov** | signed printed page 2 | — |
| **`v0.1-foundation`** | 29 Nov | repo, CI, compose, migration, UI scaffold, engine skeleton, data models | ~8% |
| `M1` | 6 Dec | OSM/OCM ingest, range + criteria, Field forms, pilot survey and first visit | ~16% |
| **`v0.5-engine-data`** | 27 Dec | scoring, queue model, `recommend()`, loaders, API read + field + recommend, census and survey in progress | ~32% |
| `M3` | 3 Jan | UI complete, e2e, API tests, field data processed, BWM + queue calibration | ~38% |
| **`v1.0-phase1`** | 10 Jan | everything in Phase-I, final report | **40%** |

The percentages are targets for the Friday completion check.

## Weekly grid: the pull requests expected to merge each week
| Week | Ansh | Atharva | Yash | Anshuman | Kashish | Eshwari |
|---|---|---|---|---|---|---|
| W1 | handles, compose, API skeleton, CI, tag | engine skeleton | DB models | UI scaffold + mocks | protocol, ethics, instruments | literature start |
| W2 | OSRM | range + criteria | OSM, OCM + dedupe | census + survey + queue forms | pilot, first census | Vahan export + data sources |
| W3 | seed hook | scoring + modes | loaders | forms connected | census batch 1 | districts + policy, literature draft |
| W4 | e2e skeleton | queue + recommend() | data quality, read + field API | recommend page | census corridors | corridor spacing |
| W5 | integration + `v0.5` | simulator regression | recommend API | compare panel + detail | survey, queue observation | report skeleton |
| W6 | e2e scenario | calibration + survey weights | API tests + perf | polish + tests | analysis scripts | figures + contributions |
| W7 | demo + `v1.0` | ENGINE.md + final runs | data snapshot | demo recording | field results | final report |

## Rules for `main`
1. Linear history: **squash and merge** only.
2. Every commit on `main` is a PR title in Conventional Commits format with the issue number.
3. `main` must always run: `docker compose up` works at every tag.
4. If `main` breaks, the author of the last merge and its reviewer fix it first, before any other work.
5. No force pushes. Mistakes are fixed forward with a new commit.
