# CERCOS — Antigravity start prompts: Kashish

How to use
1. Work from a **clone of https://github.com/anshere0/CERCOS.git**, not from an unzipped copy: `git clone https://github.com/anshere0/CERCOS.git` then `cd CERCOS`. Open exactly that folder in Antigravity.
2. Start a **new conversation in Planning mode**.
3. Copy everything under the line below into the first message. Read the plan, then approve.
4. After the agent finishes, read the diff yourself, run the verification commands, then push the branch, open the PR and request Eshwari.

---

### PROMPT 1 of 1 — Field protocol, ethics and instruments (Task 1; later tasks use the generic NEXT-TASK prompt in START_HERE.md)

PRE-FLIGHT — do this first, report the results, and change NOTHING yet
1. Run: pwd ; git rev-parse --show-toplevel ; git remote -v ; git branch --show-current ; git status --short
2. Confirm these exist at the workspace root: TEAM.md, CONTRIBUTING.md, AGENTS.md, PROJECT_MANIFEST.yaml, contracts/, config/, docs/team/kashish.md
3. Run: find . -name AGENTS.md -not -path "*/node_modules/*" . There must be exactly ONE.
4. STOP and tell me, instead of continuing, if any of these is true: this folder is not a git repository (it was unzipped instead of cloned); origin is not https://github.com/anshere0/CERCOS.git; the workspace root is not the CERCOS repo root; more than one AGENTS.md exists.
5. If I am on main, create the branch `docs/field-protocol-ethics` from an up-to-date main. Never commit on main.

ROLE
You are assisting Kashish, who leads the field research of CERCOS (census, user survey, queue observation). This session produces documents only. You are a drafting assistant: you do not decide ethics, approvals, or sample numbers, and you never invent them.

READ FIRST
docs/team/kashish.md, docs/FIELD_FORMS.md, contracts/schema.sql (tables survey_responses, station_observations, charging_stations, connectors), config/weights.yaml, PROJECT_MANIFEST.yaml (research_questions).

OWNED FOLDERS (edit only these)
docs/FIELD_FORMS.md, docs/FIELD_PROTOCOL.md, docs/ETHICS.md, data/field/processed/ (nothing goes there yet), analysis/ (not in this task).
Never create anything in data/field/raw/ or data/field/photos/; those are git-ignored.

TASK (branch docs/field-protocol-ethics)
1. Rewrite docs/FIELD_FORMS.md as three final instruments, each as a table: field name, question wording, type, allowed values, required, and the database column it maps to in contracts/schema.sql (add a "mapping check" column; list any field with no column as an issue for Yash instead of changing the schema).
   - Census: one row per station (name, operator, GPS, connectors with type and kW, posted tariff, hours, working yes/no, payment method, notes, enumerator).
   - Survey: consent first; segment E2W/E3W/E4W; vehicle model; home charging; range anxiety 1-5; the Best-Worst task over six criteria (detour, cost, wait, speed, rating, battery safety): pick best, pick worst, rate each other criterion against the best and against the worst on a 1-9 scale (9 distinct comparisons); willingness to pay extra per kWh for zero wait. Include the exact respondent-facing wording in simple English and Hindi (mark the Hindi as "needs native-speaker check"). No names, phone numbers or faces.
   - Queue sheet: station, slot (07-10, 12-15, 18-21), 15-minute intervals with arrivals, vehicles waiting, connectors busy, and session start/end times.
2. Write docs/FIELD_PROTOCOL.md: zones (Bhopal city; Bhopal-Sehore-Ashta; Bhopal-Vidisha-Sanchi; Bhopal-Narmadapuram-Raisen), the pairs and visit roster from TEAM.md, a step-by-step visit procedure, rules at the station (ask permission, never touch equipment, never photograph people), targets (>= 40 stations or all that exist, >= 60 respondents with about 20 per segment, >= 8 stations x 3 slots), data handling (raw on a shared drive with backup, only anonymised files in Git), and a record-book entry template.
3. Write docs/ETHICS.md as a DRAFT for faculty review: a short consent text read aloud, what is collected and not collected, storage, access, deletion date placeholder. Put at the top of the survey section and of ETHICS.md: "DRAFT - not approved. Approved by: ________ Date: ________". Do not claim approval has been given.
4. Add a Google Forms build sheet (section order, question types) to docs/FIELD_FORMS.md so the team can use Google Forms until Anshuman's forms ship.
5. End docs/FIELD_FORMS.md with a "Handoff to Anshuman" list of final field names and types.
Acceptance: every field maps to a column or is listed as an issue; the survey has exactly 9 distinct Best-Worst comparisons described correctly; nothing claims approvals that do not exist.

COMMITS (in order)
docs(field): add field protocol
docs(field): add ethics and consent text
docs(field): finalise instruments

NEXT: after faculty approval and the pilot, the next code task is analysis/bwm_weights.py (see docs/team/kashish.md).

WORKING RULES (apply for the whole session)
- I am Kashish, a peer in a six-person team. Read AGENTS.md, TEAM.md and CONTRIBUTING.md first and follow them.
- Edit ONLY the folders listed under OWNED FOLDERS. If something outside them must change, do not edit it: write the request as a short issue text for the owner and show it to me.
- Never run git push, never open or merge a PR, never touch main. I will push after I have read the diff.
- Never fabricate real-world data, references, approvals, or numbers. Anything simulated or assumed is labelled `synthetic` or `assumption`.
- Never commit secrets (.env), raw survey data, or photos of people.
- Use Planning mode: produce an Implementation Plan artifact first and WAIT for my approval before writing code or files.
- Make small commits using exactly the commit messages listed below (Conventional Commits).
- I must be able to explain every line at a viva. After you finish, explain each new file in 2-3 plain sentences.

WHEN FINISHED, print
1. the list of commits; 2. the exact commands I should run to verify the work myself; 3. a draft pull-request description that follows .github/pull_request_template.md and ends with `Closes #<issue number>`; 4. what my reviewer (Eshwari; secondary Atharva) should check; 5. anything you assumed or could not do. Then STOP.

---
