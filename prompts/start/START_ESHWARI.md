# CERCOS — Antigravity start prompts: Eshwari

How to use
1. Work from a **clone of https://github.com/anshere0/CERCOS.git**, not from an unzipped copy: `git clone https://github.com/anshere0/CERCOS.git` then `cd CERCOS`. Open exactly that folder in Antigravity.
2. Start a **new conversation in Planning mode**.
3. Copy everything under the line below into the first message. Read the plan, then approve.
4. After the agent finishes, read the diff yourself, run the verification commands, then push the branch, open the PR and request Kashish.

---

### PROMPT 1 of 1 — Verified reading list and references (Task 1; later tasks use the generic NEXT-TASK prompt in START_HERE.md)

PRE-FLIGHT — do this first, report the results, and change NOTHING yet
1. Run: pwd ; git rev-parse --show-toplevel ; git remote -v ; git branch --show-current ; git status --short
2. Confirm these exist at the workspace root: TEAM.md, CONTRIBUTING.md, AGENTS.md, PROJECT_MANIFEST.yaml, contracts/, config/, docs/team/eshwari.md
3. Run: find . -name AGENTS.md -not -path "*/node_modules/*" . There must be exactly ONE.
4. STOP and tell me, instead of continuing, if any of these is true: this folder is not a git repository (it was unzipped instead of cloned); origin is not https://github.com/anshere0/CERCOS.git; the workspace root is not the CERCOS repo root; more than one AGENTS.md exists.
5. If I am on main, create the branch `docs/literature-start` from an up-to-date main. Never commit on main.

ROLE
You are assisting Eshwari, who owns the literature, policy data and report of CERCOS. This session builds the reading list and verified reference file. References are graded work: a made-up or wrong citation is a serious failure. You may use the browser to open publisher pages and DOIs.

READ FIRST
docs/team/eshwari.md, docs/CANDIDATE_REFERENCES.md (candidate list; some entries are marked (v) because they are less certain), PROJECT_MANIFEST.yaml (research_questions), docs/DATA_SOURCES.md.

OWNED FOLDERS (edit only these)
docs/LITERATURE.md, docs/references.bib, docs/references_unverified.md, docs/CANDIDATE_REFERENCES.md, docs/DATA_SOURCES.md. Nothing else.

HARD RULES FOR REFERENCES
- Never add a reference from memory. For each candidate, open the publisher page, the DOI, or an official source and compare authors, year, title, journal or book, volume, pages.
- If everything matches, add it to docs/references.bib with a `note` field: "verified <date> at <URL>".
- If anything is wrong, fix it ONLY from what the page shows and record the correction. If you cannot open or confirm it, do NOT put it in references.bib; list it in docs/references_unverified.md with the reason.
- Official documents (Ministry of Power guidelines, BEE guidelines, MP EV Policy 2025, Ministry of Heavy Industries Rajya Sabha Unstarred Question 3910 of 27 March 2026) must be cited with the exact title, date and URL you opened.
- In the comparison table, fill "what it misses" only from what you actually read (abstract or full text). Mark each row "source read: abstract only" or "full text". Do not pretend to have read full papers. Eshwari must read the important ones herself.

TASK (branch docs/literature-start)
1. Verify every entry in docs/CANDIDATE_REFERENCES.md as above. Report counts: verified, corrected, unverified.
2. Create docs/references.bib (verified only) and docs/references_unverified.md.
3. Create docs/LITERATURE.md with a comparison table: reference, method, vehicle types covered, criteria used, data used, what it misses, source-read flag. Group by: MCDM and rank reversal; EV routing and charging stops; charger siting and coverage; queueing; range anxiety and user behaviour; India and Madhya Pradesh policy.
4. At the bottom of docs/LITERATURE.md add a "Gap statement (DRAFT for Eshwari to rewrite)" that states only gaps supported by the table plus the official statement in the Ministry of Heavy Industries reply, quoting it with a short quote under 15 words only if you opened the document.
5. Report how many verified references we have versus the target of 30 and suggest search terms for finding the rest.
Acceptance: every entry in references.bib has a verification note; no unverified entries in it; the table never claims more than the source read.

COMMITS (in order)
docs(report): add reading list and comparison table
docs(report): add verified references.bib

NEXT: Task 2 is the Vahan export steps and data sources (see docs/team/eshwari.md). She does the dashboard export by hand; no scraping.

WORKING RULES (apply for the whole session)
- I am Eshwari, a peer in a six-person team. Read AGENTS.md, TEAM.md and CONTRIBUTING.md first and follow them.
- Edit ONLY the folders listed under OWNED FOLDERS. If something outside them must change, do not edit it: write the request as a short issue text for the owner and show it to me.
- Never run git push, never open or merge a PR, never touch main. I will push after I have read the diff.
- Never fabricate real-world data, references, approvals, or numbers. Anything simulated or assumed is labelled `synthetic` or `assumption`.
- Never commit secrets (.env), raw survey data, or photos of people.
- Use Planning mode: produce an Implementation Plan artifact first and WAIT for my approval before writing code or files.
- Make small commits using exactly the commit messages listed below (Conventional Commits).
- I must be able to explain every line at a viva. After you finish, explain each new file in 2-3 plain sentences.

WHEN FINISHED, print
1. the list of commits; 2. the exact commands I should run to verify the work myself; 3. a draft pull-request description that follows .github/pull_request_template.md and ends with `Closes #<issue number>`; 4. what my reviewer (Kashish; secondary Ansh) should check; 5. anything you assumed or could not do. Then STOP.

---
