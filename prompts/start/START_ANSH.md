# CERCOS — Antigravity start prompts: Ansh

How to use
1. Work from a **clone of https://github.com/anshere0/CERCOS.git**, not from an unzipped copy: `git clone https://github.com/anshere0/CERCOS.git` then `cd CERCOS`. Open exactly that folder in Antigravity.
2. Start a **new conversation in Planning mode**.
3. Copy everything under the line below into the first message. Read the plan, then approve.
4. After the agent finishes, read the diff yourself, run the verification commands, then push the branch, open the PR and request Atharva.

---

### PROMPT 1 of 2 — Docker Compose, Makefile, requirements

PRE-FLIGHT — do this first, report the results, and change NOTHING yet
1. Run: pwd ; git rev-parse --show-toplevel ; git remote -v ; git branch --show-current ; git status --short
2. Confirm these exist at the workspace root: TEAM.md, CONTRIBUTING.md, AGENTS.md, PROJECT_MANIFEST.yaml, contracts/, config/, docs/team/ansh.md
3. Run: find . -name AGENTS.md -not -path "*/node_modules/*" . There must be exactly ONE.
4. STOP and tell me, instead of continuing, if any of these is true: this folder is not a git repository (it was unzipped instead of cloned); origin is not https://github.com/anshere0/CERCOS.git; the workspace root is not the CERCOS repo root; more than one AGENTS.md exists.
5. If I am on main, create the branch `feat/infra-compose` from an up-to-date main. Never commit on main.

ROLE
You are assisting Ansh with P0 Foundation of CERCOS (EPICS project). His area is repository infrastructure; it is a service to the team, not authority over anyone's work. Everyone is waiting for this, so correctness matters more than extras.

READ FIRST
docs/team/ansh.md, .env.example, contracts/schema.sql, .github/workflows/ci.yml, CONTRIBUTING.md section 8.

OWNED FOLDERS (edit only these)
docker-compose.yml, Makefile, backend/requirements.txt, backend/Dockerfile, db/, scripts/, tests/e2e/, .github/ (do not change the content of CODEOWNERS yet).
DO NOT create anything inside frontend/ (Anshuman owns it). The guide mentions frontend/Dockerfile: ignore that. Use the node:20 image directly.

TASK (branch feat/infra-compose)
1. docker-compose.yml with three services:
   - db: image postgis/postgis:16-3.4, env from .env (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB), a named volume, healthcheck with pg_isready.
   - api: build ./backend (backend/Dockerfile, python:3.12-slim), port 8000, uvicorn with reload, mounts the repo root at /app so contracts/ and config/ are readable, depends_on db with condition service_healthy, env DATABASE_URL from .env.
   - web: image node:20, port 5173, mounts ./frontend, working dir /app. Command: if package.json exists run npm ci or npm install then `npm run dev -- --host 0.0.0.0`, otherwise print "frontend not scaffolded yet" and sleep. It must not fail while frontend/ is empty.
2. backend/requirements.txt with: fastapi, uvicorn[standard], sqlalchemy>=2, alembic, psycopg[binary], geoalchemy2, pydantic, pydantic-settings, numpy, pyyaml, pytest, ruff, httpx. (numpy and pyyaml are needed by Atharva's engine; geoalchemy2 by Yash's models; they must be here or CI breaks.)
3. backend/Dockerfile (python:3.12-slim, installs requirements, runs uvicorn app.main:app).
4. Makefile targets: up (docker compose up -d --build), down, test (pytest backend/tests -q with PYTHONPATH=backend), lint (ruff check backend), seed (placeholder that prints "seed hook arrives in P1" and exits 0), psql (docker compose exec db psql with the .env user/db). Add `.PHONY`.
5. Add the line `data/osrm/` to .gitignore.
6. Document in README.md only the 3-line quick start (cp .env.example .env; make up; open http://localhost:8000/health after Task 2).
Acceptance: `cp .env.example .env && docker compose config` is valid; `make up` starts db healthy; `make lint` and `make test` do not crash on the empty backend (tests may report "no tests ran").

COMMITS (in order)
feat(infra): add docker-compose with postgis, api, web
feat(infra): add Makefile targets
docs(infra): add setup steps to README

WORKING RULES (apply for the whole session)
- I am Ansh, a peer in a six-person team. Read AGENTS.md, TEAM.md and CONTRIBUTING.md first and follow them.
- Edit ONLY the folders listed under OWNED FOLDERS. If something outside them must change, do not edit it: write the request as a short issue text for the owner and show it to me.
- Never run git push, never open or merge a PR, never touch main. I will push after I have read the diff.
- Never fabricate real-world data, references, approvals, or numbers. Anything simulated or assumed is labelled `synthetic` or `assumption`.
- Never commit secrets (.env), raw survey data, or photos of people.
- Use Planning mode: produce an Implementation Plan artifact first and WAIT for my approval before writing code or files.
- Make small commits using exactly the commit messages listed below (Conventional Commits).
- I must be able to explain every line at a viva. After you finish, explain each new file in 2-3 plain sentences.

WHEN FINISHED, print
1. the list of commits; 2. the exact commands I should run to verify the work myself; 3. a draft pull-request description that follows .github/pull_request_template.md and ends with `Closes #<issue number>`; 4. what my reviewer (Atharva; secondary Yash) should check; 5. anything you assumed or could not do. Then STOP.

---

### PROMPT 2 of 2 — FastAPI skeleton and migration 0001 (paste after PR 1 is merged)

PRE-FLIGHT — do this first, report the results, and change NOTHING yet
1. Run: pwd ; git rev-parse --show-toplevel ; git remote -v ; git branch --show-current ; git status --short
2. Confirm these exist at the workspace root: TEAM.md, CONTRIBUTING.md, AGENTS.md, PROJECT_MANIFEST.yaml, contracts/, config/, docs/team/ansh.md
3. Run: find . -name AGENTS.md -not -path "*/node_modules/*" . There must be exactly ONE.
4. STOP and tell me, instead of continuing, if any of these is true: this folder is not a git repository (it was unzipped instead of cloned); origin is not https://github.com/anshere0/CERCOS.git; the workspace root is not the CERCOS repo root; more than one AGENTS.md exists.
5. If I am on main, create the branch `feat/api-skeleton` from an up-to-date main. Never commit on main.

ROLE
Same role and rules as Prompt 1. Start from an up-to-date main that already contains the compose file.

READ FIRST
contracts/schema.sql, contracts/openapi.draft.yaml, docker-compose.yml, backend/requirements.txt.

OWNED FOLDERS
backend/app/main.py, backend/app/core/, db/, backend/tests/api/test_health.py, backend/pytest.ini. Do not edit models, schemas, api routes, mcdm or queue (other owners).

TASK (branch feat/api-skeleton)
1. backend/app/main.py: FastAPI app with GET /health returning {"status": "ok"}; backend/app/__init__.py.
2. backend/app/core/config.py reading DATABASE_URL and OSRM_URL from the environment with pydantic-settings.
3. backend/pytest.ini containing: [pytest] / pythonpath = . / testpaths = tests  (this lets everyone import `app.*` in tests; tell the team in your summary).
4. Alembic: db/alembic.ini and db/migrations/env.py reading DATABASE_URL from the environment; migration db/migrations/versions/0001_initial.py whose upgrade() executes the SQL read from contracts/schema.sql with op.execute (do NOT retype the schema); downgrade() drops schema cercos CASCADE.
5. backend/tests/api/test_health.py using FastAPI TestClient.
Acceptance: docker compose run --rm api alembic -c db/alembic.ini upgrade head succeeds; `make psql` then \dt cercos.* lists 8 tables; curl localhost:8000/health returns ok; pytest passes.
Remind me to ask Yash to review the migration column by column.

COMMITS (in order)
feat(api): add FastAPI app with /health
feat(db): configure alembic
feat(db): migration 0001 from contracts/schema.sql
test(api): add health test

WORKING RULES (apply for the whole session)
- I am Ansh, a peer in a six-person team. Read AGENTS.md, TEAM.md and CONTRIBUTING.md first and follow them.
- Edit ONLY the folders listed under OWNED FOLDERS. If something outside them must change, do not edit it: write the request as a short issue text for the owner and show it to me.
- Never run git push, never open or merge a PR, never touch main. I will push after I have read the diff.
- Never fabricate real-world data, references, approvals, or numbers. Anything simulated or assumed is labelled `synthetic` or `assumption`.
- Never commit secrets (.env), raw survey data, or photos of people.
- Use Planning mode: produce an Implementation Plan artifact first and WAIT for my approval before writing code or files.
- Make small commits using exactly the commit messages listed below (Conventional Commits).
- I must be able to explain every line at a viva. After you finish, explain each new file in 2-3 plain sentences.

WHEN FINISHED, print
1. the list of commits; 2. the exact commands I should run to verify the work myself; 3. a draft pull-request description that follows .github/pull_request_template.md and ends with `Closes #<issue number>`; 4. what my reviewer (Atharva; secondary Yash) should check; 5. anything you assumed or could not do. Then STOP.

---
