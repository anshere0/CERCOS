# CERCOS — Cognitive EV Route & Charging Optimization System
EPICS Phase-I project (VIT Bhopal). Six teammates, one repository: https://github.com/anshere0/CERCOS

CERCOS recommends the **best** EV charging stop (not the nearest) for Madhya Pradesh drivers using multi-criteria decision making, and produces measured charging-gap analytics for planners.

## Start here
1. Everyone reads `TEAM.md`, `CONTRIBUTING.md` and **their own guide** in `docs/team/`.
2. First-time setup (done once, on a call with all six, by the repository owner):
```bash
unzip CERCOS-team-pack.zip && cd CERCOS
git init
git add .
git commit -m "chore: bootstrap team pack"
git branch -M main
git remote add origin https://github.com/anshere0/CERCOS.git
git push -u origin main          # the ONLY direct push to main, ever
```
3. Immediately apply the branch ruleset (`CONTRIBUTING.md` §8) so that `main` is protected for everyone.
4. Run `bash scripts/set_handles.sh <six GitHub usernames>`, merge that change by PR, then run `bash scripts/bootstrap_github.sh`.
5. Everyone: `git clone`, set `git config user.name` and `user.email`, copy `.env.example` to `.env`, open the repo in Antigravity.

## Map of the repository
| Path | Owner | Purpose |
|---|---|---|
| `backend/app/mcdm`, `backend/app/queue`, `research/` | Atharva | engine, queue model, simulation |
| `backend/app/etl`, `api`, `models`, `schemas`, `db/seeds` | Yash | data pipelines and API |
| `frontend/` | Anshuman | map app and Field Mode |
| `analysis/`, `data/field/` | Kashish | field research and analysis |
| `docs/`, `data/vahan`, `data/policy` | Eshwari | literature, policy data, report |
| `docker-compose.yml`, `Makefile`, `db/`, `.github/`, `tests/e2e`, `scripts/` | Ansh | infrastructure and integration |
| `contracts/`, `config/` | shared (two approvals) | API, schema, engine interface, weights |

## Key files
`PROJECT_MANIFEST.yaml` (scope and phases) · `AGENTS.md` (rules for Antigravity agents) · `ANTIGRAVITY_MASTER_PROMPT.md` · `prompts/` · `docs/team/COMMIT_PLAN.md` · `docs/team/HANDOFFS.md` · `docs/team/COMPLETION_CHECKLIST.md`

## Honesty rule
Pilot results in `research/` use **synthetic** data and validate the method only. Real findings come from the field data. Label everything accordingly.
