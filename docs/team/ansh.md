# ANSH — Repository, Infrastructure & Integration  (6% of the 40%)

**Mission:** every other member can clone the repo, run `make up`, and see a working database, API and web shell by **29 Nov**, and the finished pieces always connect.
Your area is plumbing. It is a service to the whole team and carries no authority over anyone's work. Your own PRs are reviewed by **Atharva** (primary) and **Yash** (secondary). You review **Anshuman** (primary) and **Eshwari** (secondary).

## You own
`docker-compose.yml` · `Makefile` · `.github/` · `db/` (migrations) · `backend/app/main.py`, `backend/app/core/` · `scripts/` · `tests/e2e/` · `docs/PHASE_REPORT.md` · `docs/team/` (this folder)

## Inputs / Outputs
| You need | From | When |
|---|---|---|
| Final DB schema review | Yash | W1 |
| API endpoints to test end-to-end | Yash | W4–W5 |
| UI to test end-to-end | Anshuman | W4–W6 |
| Weekly status lines | everyone | each Friday |
| **You deliver** | | |
| Working repo, CI, compose, Makefile, migration 0001 | everyone | **29 Nov** |
| OSRM service profile | Yash | 6 Dec |
| e2e tests and release tags | everyone | W4–W7 |

## Task list by week (dates assume Week 1 = 23 Nov 2026)
**W1 (23–29 Nov)**
- [ ] **Day 1 call:** push the pack to `https://github.com/anshere0/CERCOS.git` (commands in `README.md`), then set the ruleset **together with all five others watching** (`CONTRIBUTING.md` §8).
- [ ] `bash scripts/set_handles.sh <six GitHub usernames>`; commit via PR (reviewed by Atharva); run `bash scripts/bootstrap_github.sh`.
- [ ] `docker-compose.yml`: services `db` (postgis/postgis:16-3.4), `api` (FastAPI, port 8000), `web` (Vite, port 5173). Volumes, healthchecks, `.env` usage.
- [ ] `Makefile`: `up`, `down`, `test`, `lint`, `seed`, `psql`.
- [ ] FastAPI skeleton with `GET /health`; Alembic configured; **migration 0001 = `contracts/schema.sql`**.
- [ ] CI green on `main`. Tag **`v0.1-foundation`**.
- [ ] **Bonafide:** make sure the printed page 2 is signed by the supervisor and both reviewers and delivered to Dr Ashok Kumar Patel (AB1-004-G03) **before 30 Nov**. All six sign or attend as required.

**W2 (30 Nov–6 Dec):** OSRM compose profile (Bhopal-region extract from Geofabrik; document size and the haversine×1.3 fallback). Fix anything that blocks teammates' setup.
**W3 (7–13 Dec):** `make seed` loads `db/seeds/*` fixtures (work with Yash).
**W4 (14–20 Dec):** Playwright e2e skeleton running against compose.
**W5 (21–27 Dec):** integration check of engine + data + API; tag **`v0.5-engine-data`**.
**W6 (28 Dec–3 Jan):** e2e test: Bhopal → Ashta recommendation, nearest vs CERCOS.
**W7 (4–10 Jan):** final demo build from `main`; complete `docs/PHASE_REPORT.md`; tag **`v1.0-phase1`**.

## Commit trajectory
| Branch | Commits (in order) | PR title | Reviewer | Due |
|---|---|---|---|---|
| *(first push, once)* | `chore: bootstrap team pack` | — | — | 23 Nov |
| `chore/codeowners-handles` | `chore(github): set CODEOWNERS handles` | Set real GitHub handles | Atharva | 24 Nov |
| `feat/infra-compose` | `feat(infra): add docker-compose with postgis, api, web` → `feat(infra): add Makefile targets` → `docs(infra): add setup steps to README` | Docker Compose + Makefile | Atharva | 27 Nov |
| `feat/api-skeleton` | `feat(api): add FastAPI app with /health` → `feat(db): configure alembic` → `feat(db): migration 0001 from contracts/schema.sql` → `test(api): add health test` | API skeleton + migration 0001 | Atharva (Yash checks schema) | 28 Nov |
| `fix/ci-green` *(if needed)* | `fix(ci): ...` | CI green | Atharva | 29 Nov |
| `feat/infra-osrm` | `feat(infra): add osrm profile` → `docs(infra): document extract and fallback` | OSRM profile | Atharva | 6 Dec |
| `feat/seed-hook` | `feat(infra): add make seed` | Seed hook | Atharva | 13 Dec |
| `test/e2e-skeleton` | `test(e2e): add playwright config` → `test(e2e): add smoke test` | e2e skeleton | Anshuman | 20 Dec |
| `test/e2e-bhopal-ashta` | `test(e2e): bhopal to ashta scenario` | e2e scenario | Anshuman | 3 Jan |
| `docs/phase-report-wN` *(weekly)* | `docs(report): update phase report week N` | Phase report week N | Atharva | each Fri |

## Definition of Done
- Fresh clone → `cp .env.example .env && make up` gives healthy `db`, `api`, `web`.
- `make test` and `make lint` run in CI and locally; CI is green on `main`.
- `alembic upgrade head` creates every table in `contracts/schema.sql`.
- e2e test passes in CI or documented how to run locally.
- Tags `v0.1-foundation`, `v0.5-engine-data`, `v1.0-phase1` exist.

## Antigravity prompt (Planning mode, workspace = repo root, branch `feat/infra-compose`)
```
Read AGENTS.md, TEAM.md, CONTRIBUTING.md, PROJECT_MANIFEST.yaml and contracts/schema.sql.
You work for Ansh. Edit ONLY: docker-compose.yml, Makefile, backend/app/main.py, backend/app/core/, db/, scripts/, tests/e2e/, .github/ (except CODEOWNERS content).
Task: create docker-compose.yml with services db (postgis/postgis:16-3.4 with healthcheck), api (FastAPI, uvicorn, port 8000, depends on db healthy) and web (Vite dev server, port 5173), reading from .env (see .env.example).
Create Makefile targets up, down, test, lint, seed, psql. Create backend/requirements.txt (fastapi, uvicorn, sqlalchemy>=2, alembic, psycopg[binary], pydantic, pytest, ruff, httpx), a FastAPI app with GET /health, Alembic config and migration 0001 that executes contracts/schema.sql.
Produce an implementation plan first. Write tests. Do not touch other people's folders. Do not push to main. Commit in the small steps listed in docs/team/ansh.md.
```

## Report evidence (your half page)
Describe: repository structure and CI, database migration, Docker environment, integration tests, release tags, with links to merged PRs and the tags.
