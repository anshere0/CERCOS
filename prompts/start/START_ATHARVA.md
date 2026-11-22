# CERCOS — Antigravity start prompts: Atharva

How to use
1. Work from a **clone of https://github.com/anshere0/CERCOS.git**, not from an unzipped copy: `git clone https://github.com/anshere0/CERCOS.git` then `cd CERCOS`. Open exactly that folder in Antigravity.
2. Start a **new conversation in Planning mode**.
3. Copy everything under the line below into the first message. Read the plan, then approve.
4. After the agent finishes, read the diff yourself, run the verification commands, then push the branch, open the PR and request Yash.

---

### PROMPT 1 of 1 — Engine package skeleton (Task 1; later tasks use the generic NEXT-TASK prompt in START_HERE.md)

PRE-FLIGHT — do this first, report the results, and change NOTHING yet
1. Run: pwd ; git rev-parse --show-toplevel ; git remote -v ; git branch --show-current ; git status --short
2. Confirm these exist at the workspace root: TEAM.md, CONTRIBUTING.md, AGENTS.md, PROJECT_MANIFEST.yaml, contracts/, config/, docs/team/atharva.md
3. Run: find . -name AGENTS.md -not -path "*/node_modules/*" . There must be exactly ONE.
4. STOP and tell me, instead of continuing, if any of these is true: this folder is not a git repository (it was unzipped instead of cloned); origin is not https://github.com/anshere0/CERCOS.git; the workspace root is not the CERCOS repo root; more than one AGENTS.md exists.
5. If I am on main, create the branch `feat/engine-port-research` from an up-to-date main. Never commit on main.

ROLE
You are assisting Atharva with P2 of CERCOS: the recommendation engine. This work is pure Python with no database and no network, so it can start today without waiting for anyone.

READ FIRST
docs/team/atharva.md, contracts/engine_interface.md, config/weights.yaml, config/criteria_bounds.yaml, config/vehicles.yaml, research/01_cercos_pilot_experiments.py, research/results.json.

OWNED FOLDERS (edit only these)
backend/app/mcdm/, backend/app/queue/, backend/tests/mcdm/, backend/tests/queue/, research/, config/weights.yaml, config/criteria_bounds.yaml, docs/ENGINE.md.
Do NOT create backend/requirements.txt or backend/pytest.ini (Ansh owns them and will merge them with numpy and pyyaml included). Until they exist, run tests with: PYTHONPATH=backend pytest backend/tests -q  inside a local virtual environment (pip install numpy pyyaml pytest ruff).

TASK (branch feat/engine-port-research)
1. Create the package skeleton: backend/app/__init__.py (empty, only if missing), backend/app/mcdm/{__init__,range,criteria,wsm_anchored,topsis,modes,explain,recommend,simulator}.py and backend/app/queue/{__init__,queue}.py. Modules not in this task get a docstring and `raise NotImplementedError` stubs with the signatures from contracts/engine_interface.md.
2. Port into the matching modules, behaviour unchanged: topsis (vector normalisation baseline), wsm_minmax (keep as a comparison baseline, put it in topsis.py or a clearly named function), wsm_anchored (fixed bounds), erlang_c and mmc_wq (queue/queue.py). Pure functions, type hints, docstrings with the formulas. No I/O, no database, no network inside mcdm/ or queue/.
3. Leave research/01_cercos_pilot_experiments.py working and unchanged in behaviour (it must still reproduce research/results.json).
4. Tests (write them first): backend/tests/conftest.py with a small station list and one vehicle fixture; backend/tests/queue/test_queue.py with hand-checked values: M/M/1 with lambda=0.5, mu=1 gives Wq = 1.0 hour; M/M/2 with lambda=1.5, mu=1 gives P(wait) = 0.642857 and Wq = 1.285714 hours; load a >= c returns infinity. backend/tests/mcdm/test_scoring.py: weights in config/weights.yaml sum to 1 for every mode; an alternative that is best on every criterion scores 1.0 under anchored scoring; a dominated alternative never ranks first.
5. Do not add numpy-free rewrites or extra features; stay inside the task.
Acceptance: PYTHONPATH=backend pytest backend/tests -q passes; python research/01_cercos_pilot_experiments.py still runs; ruff check backend passes.

COMMITS (in order)
refactor(engine): move pilot experiment code into mcdm package
test(engine): add pytest skeleton and fixtures

NEXT: after this PR merges, Task 2 is range.py and criteria.py (see docs/team/atharva.md).

WORKING RULES (apply for the whole session)
- I am Atharva, a peer in a six-person team. Read AGENTS.md, TEAM.md and CONTRIBUTING.md first and follow them.
- Edit ONLY the folders listed under OWNED FOLDERS. If something outside them must change, do not edit it: write the request as a short issue text for the owner and show it to me.
- Never run git push, never open or merge a PR, never touch main. I will push after I have read the diff.
- Never fabricate real-world data, references, approvals, or numbers. Anything simulated or assumed is labelled `synthetic` or `assumption`.
- Never commit secrets (.env), raw survey data, or photos of people.
- Use Planning mode: produce an Implementation Plan artifact first and WAIT for my approval before writing code or files.
- Make small commits using exactly the commit messages listed below (Conventional Commits).
- I must be able to explain every line at a viva. After you finish, explain each new file in 2-3 plain sentences.

WHEN FINISHED, print
1. the list of commits; 2. the exact commands I should run to verify the work myself; 3. a draft pull-request description that follows .github/pull_request_template.md and ends with `Closes #<issue number>`; 4. what my reviewer (Yash; secondary Ansh) should check; 5. anything you assumed or could not do. Then STOP.

---
