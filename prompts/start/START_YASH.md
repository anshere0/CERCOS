# CERCOS — Antigravity start prompts: Yash

How to use
1. Work from a **clone of https://github.com/anshere0/CERCOS.git**, not from an unzipped copy: `git clone https://github.com/anshere0/CERCOS.git` then `cd CERCOS`. Open exactly that folder in Antigravity.
2. Start a **new conversation in Planning mode**.
3. Copy everything under the line below into the first message. Read the plan, then approve.
4. After the agent finishes, read the diff yourself, run the verification commands, then push the branch, open the PR and request Anshuman.

---

### PROMPT 1 of 1 — Database models and schema drift test (Task 1; later tasks use the generic NEXT-TASK prompt in START_HERE.md)

PRE-FLIGHT — do this first, report the results, and change NOTHING yet
1. Run: pwd ; git rev-parse --show-toplevel ; git remote -v ; git branch --show-current ; git status --short
2. Confirm these exist at the workspace root: TEAM.md, CONTRIBUTING.md, AGENTS.md, PROJECT_MANIFEST.yaml, contracts/, config/, docs/team/yash.md
3. Run: find . -name AGENTS.md -not -path "*/node_modules/*" . There must be exactly ONE.
4. STOP and tell me, instead of continuing, if any of these is true: this folder is not a git repository (it was unzipped instead of cloned); origin is not https://github.com/anshere0/CERCOS.git; the workspace root is not the CERCOS repo root; more than one AGENTS.md exists.
5. If I am on main, create the branch `feat/db-models` from an up-to-date main. Never commit on main.

ROLE
You are assisting Yash with P1 of CERCOS: the database layer. The database contract already exists in contracts/schema.sql. Your models must match it exactly.

READ FIRST
docs/team/yash.md, contracts/schema.sql, contracts/openapi.draft.yaml, contracts/engine_interface.md, .agents/rules/cercos-rules.md.

OWNED FOLDERS (edit only these)
backend/app/etl/, backend/app/api/, backend/app/models/, backend/app/schemas/, backend/tests/etl/, backend/tests/api/ (except test_health.py, which is Ansh's), db/seeds/, docs/DATA_QUALITY.md, docs/API.md.
Do NOT edit db/migrations, backend/requirements.txt or backend/pytest.ini (Ansh owns them; geoalchemy2 is already on his list). Use a local virtual environment (pip install sqlalchemy geoalchemy2 pydantic pytest) and run tests with PYTHONPATH=backend pytest backend/tests -q.

TASK (branch feat/db-models)
1. backend/app/models/: SQLAlchemy 2.0 typed models (DeclarativeBase, schema="cercos") for all 8 tables in contracts/schema.sql: districts, charging_stations, connectors, vehicles, survey_responses, station_observations, recommendations_log, etl_rejects. Use GeoAlchemy2 Geometry for geom columns with the exact SRID and type from the contract, ARRAY for connector_types, JSONB for the JSON columns, and reproduce the CHECK constraints and foreign keys. Provenance columns (source, fetched_at, confidence) must be present exactly as in the contract.
2. backend/app/schemas/: Pydantic v2 models for Station (including provenance fields), Vehicle, CensusRecord, SurveyResponse (consent must be True or validation fails; no name or phone fields anywhere), QueueObservation.
3. Tests, no live database needed: backend/tests/etl/test_schema_drift.py parses contracts/schema.sql (CREATE TABLE blocks) and asserts that every table and column name in the SQL exists in the SQLAlchemy metadata and vice versa, so any future drift fails CI. Plus tests that SurveyResponse rejects consent=False and that Station requires source and confidence.
4. Write a short docs/API.md stub listing the planned endpoints from contracts/openapi.draft.yaml (no implementation yet).
Acceptance: PYTHONPATH=backend pytest backend/tests -q passes; ruff check backend passes; the drift test fails when I deliberately rename a column in a models file (show me this once).

COMMITS (in order)
feat(db): add SQLAlchemy models from contract
test(db): model smoke tests

ALSO (not code): in your summary, give me a short checklist to review Ansh's migration 0001 against contracts/schema.sql column by column, because that review is my job this week.
NEXT: Task 2 is the OpenStreetMap loader (see docs/team/yash.md).

WORKING RULES (apply for the whole session)
- I am Yash, a peer in a six-person team. Read AGENTS.md, TEAM.md and CONTRIBUTING.md first and follow them.
- Edit ONLY the folders listed under OWNED FOLDERS. If something outside them must change, do not edit it: write the request as a short issue text for the owner and show it to me.
- Never run git push, never open or merge a PR, never touch main. I will push after I have read the diff.
- Never fabricate real-world data, references, approvals, or numbers. Anything simulated or assumed is labelled `synthetic` or `assumption`.
- Never commit secrets (.env), raw survey data, or photos of people.
- Use Planning mode: produce an Implementation Plan artifact first and WAIT for my approval before writing code or files.
- Make small commits using exactly the commit messages listed below (Conventional Commits).
- I must be able to explain every line at a viva. After you finish, explain each new file in 2-3 plain sentences.

WHEN FINISHED, print
1. the list of commits; 2. the exact commands I should run to verify the work myself; 3. a draft pull-request description that follows .github/pull_request_template.md and ends with `Closes #<issue number>`; 4. what my reviewer (Anshuman; secondary Atharva) should check; 5. anything you assumed or could not do. Then STOP.

---
