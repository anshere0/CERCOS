# CONTRIBUTING — rules for all six members

## 1. Golden rules
1. `main` is protected. **Nothing is pushed to `main`.** Everything arrives through a pull request (PR).
2. **One issue → one branch → one PR.** Small PRs (under about 300 changed lines) are reviewed faster and rejected less.
3. **The author never merges their own PR.** The reviewer merges (squash and merge) after approving and CI is green.
4. **Run it before you approve it.** Check out the branch, run `make test`, try the feature.
5. **Your own folders only** (see `.github/CODEOWNERS`). Cross-area work needs an issue and the owner's agreement.

## 2. Daily workflow
```bash
git switch main && git pull
git switch -c feat/engine-range-model          # branch name: <type>/<area>-<short-name>
# ... work with Antigravity or by hand ...
make test && make lint                         # must pass locally (available after Ansh's foundation PR)
git add <files>                                # never `git add .` blindly - check `git status`
git commit -m "feat(engine): add range model with 8% reserve"
git push -u origin feat/engine-range-model
# open a PR on GitHub, fill the template, request the primary reviewer, link the issue with "Closes #12"
```
Set your identity once: `git config user.name "Your Name"` and `git config user.email "<the email on your GitHub account>"`. Every commit must show your own account.

## 3. Commit message format (Conventional Commits)
`<type>(<area>): <imperative summary>` — types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `data`.
Areas: `infra`, `db`, `engine`, `queue`, `etl`, `api`, `ui`, `field`, `analysis`, `report`, `ci`.
Examples: `feat(etl): add Overpass loader for Bhopal region` · `test(engine): rank reversal stays at 0 percent` · `data(field): add anonymised census batch 1`.
One logical change per commit. Commit at least every working session. Never commit "misc" or "final".

## 4. Pull request rules
- Fill the PR template honestly. Attach a screenshot or recording for anything visible.
- Reviewer follows the **reviewer checklist**: check out the branch, run it, ask the author to explain one function, check tests, check for secrets and large files.
- Use **Request changes** with specific comments. Authors fix, push, and reply. Reviewers re-check.
- Merge method: **squash and merge**; delete the branch afterwards.
- Changes to `contracts/`, `config/`, `AGENTS.md` and `PROJECT_MANIFEST.yaml` need approval from **two** people from different areas.

## 5. Definition of Done (for every issue)
Merged PR linked to the issue · CI green · tests included · reviewer ran it · docs updated · owner added a line to their weekly log · issue closed.
**An issue that is not merged is not done**, whatever is on someone's laptop.

## 6. Blockers and late work
- Post the blocker in the group chat within 24 hours with: what is blocked, who can unblock it.
- Work more than 2 days late: the owner and primary reviewer pair up and re-plan.
- Work more than 5 days late: the team splits the remaining task across people with spare capacity at the next Monday meeting. Everyone keeps credit for what they did, and the log records who did what.

## 7. Weekly rhythm
| When | What |
|---|---|
| Monday | 20-minute meeting: last week done, this week planned, blockers. Rotating facilitator. |
| Within 24 h | Reviews |
| Friday | Demo from `main` + completion check against `docs/team/COMPLETION_CHECKLIST.md` |
| Weekly | Supervisor signs the record book; each person updates `docs/team/logs/<name>.md` |

## 8. Repository setup (one-time, done together on a call)
The repository owner has the admin screens, so they click through them while **everyone watches and verifies**:
1. Settings → Collaborators: add all five others with **Write** role.
2. Settings → Rules → Rulesets → New branch ruleset → target: default branch.
   - Restrict deletions · Block force pushes
   - Require a pull request: 1 approval, dismiss stale approvals, **require review from Code Owners**, require conversation resolution
   - Require status checks: `backend`, `frontend`, `research-script`, `config-valid`, `secrets-scan`
   - **Bypass list: empty.** The owner is bound like everyone else.
3. Run `bash scripts/set_handles.sh ...` and then `bash scripts/bootstrap_github.sh` (needs `gh auth login`).
4. Create a GitHub Project (Board) with columns Todo, In progress, In review, Done and add all issues.
5. If rulesets are unavailable on your plan, apply the GitHub Student Developer Pack for Pro, or make the repository public.

## 9. Using Antigravity
- Open the repo as the workspace. `AGENTS.md` and `.agents/rules` load automatically.
- One agent session = one person = one branch = one area.
- Start in **Planning mode**, read the plan, then approve. Never accept a plan that edits other people's folders.
- Ask the agent to write tests first. Read every diff before you commit.
- Anything simulated must be labelled `synthetic`.
