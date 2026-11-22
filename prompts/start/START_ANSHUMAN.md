# CERCOS — Antigravity start prompts: Anshuman

How to use
1. Work from a **clone of https://github.com/anshere0/CERCOS.git**, not from an unzipped copy: `git clone https://github.com/anshere0/CERCOS.git` then `cd CERCOS`. Open exactly that folder in Antigravity.
2. Start a **new conversation in Planning mode**.
3. Copy everything under the line below into the first message. Read the plan, then approve.
4. After the agent finishes, read the diff yourself, run the verification commands, then push the branch, open the PR and request Ansh.

---

### PROMPT 1 of 1 — Frontend scaffold, base map and mock API (Task 1; later tasks use the generic NEXT-TASK prompt in START_HERE.md)

PRE-FLIGHT — do this first, report the results, and change NOTHING yet
1. Run: pwd ; git rev-parse --show-toplevel ; git remote -v ; git branch --show-current ; git status --short
2. Confirm these exist at the workspace root: TEAM.md, CONTRIBUTING.md, AGENTS.md, PROJECT_MANIFEST.yaml, contracts/, config/, docs/team/anshuman.md
3. Run: find . -name AGENTS.md -not -path "*/node_modules/*" . There must be exactly ONE.
4. STOP and tell me, instead of continuing, if any of these is true: this folder is not a git repository (it was unzipped instead of cloned); origin is not https://github.com/anshere0/CERCOS.git; the workspace root is not the CERCOS repo root; more than one AGENTS.md exists.
5. If I am on main, create the branch `feat/ui-scaffold` from an up-to-date main. Never commit on main.

ROLE
You are assisting Anshuman with the P4 frontend of CERCOS. He builds against mocks so he never waits for the backend.

READ FIRST
docs/team/anshuman.md, contracts/openapi.draft.yaml, contracts/engine_interface.md, docs/FIELD_FORMS.md, .github/workflows/ci.yml (the frontend job runs: cd frontend && npm ci && npm run build).

OWNED FOLDERS (edit only these)
frontend/ and docs/UI.md. Touch nothing else. In particular do not create a Dockerfile anywhere; Ansh's compose file runs the frontend with the node:20 image.

TASK (branch feat/ui-scaffold)
1. Inside frontend/ scaffold Vite + React + TypeScript (npm create vite@latest . -- --template react-ts). Keep package-lock.json committed (CI uses npm ci). Package scripts must include dev, build, lint, test.
2. Dependencies: leaflet, react-leaflet, @types/leaflet; dev: vitest, @testing-library/react, jsdom, msw, openapi-typescript, vite-plugin-pwa (install the PWA plugin but only configure it later).
3. Map: OpenStreetMap tiles in Leaflet centred on Bhopal (about 23.26 N, 77.41 E), zoom 11, visible OpenStreetMap attribution, full-height responsive layout that works at 360 px width.
4. Types and client: generate src/api/types.ts with openapi-typescript from ../contracts/openapi.draft.yaml; write src/api/client.ts with typed functions for /v1/modes, /v1/vehicles, /v1/stations, /v1/recommend, /v1/field/*; the base URL comes from VITE_API_URL.
5. Mocks: MSW handlers in src/mocks/ returning data shaped exactly like contracts/engine_interface.md (a recommend result with top3, explain, warnings and source badges). Controlled by VITE_USE_MOCKS=true. When mocks are on, show a small visible banner "Mock data". Add frontend/.env.example (VITE_API_URL, VITE_USE_MOCKS).
6. One Vitest smoke test that renders the app and finds the map container.
Acceptance: cd frontend && npm ci && npm run build && npm run lint && npm test all pass; npm run dev shows the Bhopal map and the Mock banner.

COMMITS (in order)
feat(ui): scaffold vite react typescript
feat(ui): base map centred on bhopal
feat(ui): typed api client and mocks

Take screenshots of the running app for the PR (tell me exactly which views).
NEXT: Task 2 is the census form (see docs/team/anshuman.md); first get the final field list from Kashish.

WORKING RULES (apply for the whole session)
- I am Anshuman, a peer in a six-person team. Read AGENTS.md, TEAM.md and CONTRIBUTING.md first and follow them.
- Edit ONLY the folders listed under OWNED FOLDERS. If something outside them must change, do not edit it: write the request as a short issue text for the owner and show it to me.
- Never run git push, never open or merge a PR, never touch main. I will push after I have read the diff.
- Never fabricate real-world data, references, approvals, or numbers. Anything simulated or assumed is labelled `synthetic` or `assumption`.
- Never commit secrets (.env), raw survey data, or photos of people.
- Use Planning mode: produce an Implementation Plan artifact first and WAIT for my approval before writing code or files.
- Make small commits using exactly the commit messages listed below (Conventional Commits).
- I must be able to explain every line at a viva. After you finish, explain each new file in 2-3 plain sentences.

WHEN FINISHED, print
1. the list of commits; 2. the exact commands I should run to verify the work myself; 3. a draft pull-request description that follows .github/pull_request_template.md and ends with `Closes #<issue number>`; 4. what my reviewer (Ansh; secondary Yash) should check; 5. anything you assumed or could not do. Then STOP.

---
