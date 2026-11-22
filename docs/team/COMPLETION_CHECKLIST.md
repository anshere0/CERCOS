# COMPLETION CHECKLIST — run it at every Friday demo

A task is **Done** only when all boxes are ticked. Anything else is "In progress", whatever a laptop shows.

## Per task
- [ ] PR merged into `main` (squash) and linked to its issue
- [ ] CI green on `main` after the merge
- [ ] Reviewer ran the branch and approved
- [ ] Tests included for new logic
- [ ] Docs updated; owner's weekly log updated
- [ ] Demo shown to the team on Friday (screen share from `main`)

## Per week
- [ ] Each person logged ≥ 6 hours in the record book and `docs/team/logs/`
- [ ] The supervisor signed the record book
- [ ] `docs/PHASE_REPORT.md` updated (done, mocked, next week)
- [ ] No open PR older than 48 hours
- [ ] No blocker older than 24 hours

## Per phase
| Phase | Check |
|---|---|
| P0 | `make up` works from a fresh clone; migration applies; CI green |
| P1 | Loaders idempotent; provenance on all rows; data-quality report published |
| P2 | `recommend()` passes contract tests for 6 modes × 4 segments; rank reversal 0%; Erlang-C verified |
| P3 | Counts met (stations, respondents, queue slots) or shortfall explained; no raw data in Git; BWM reproduces the worked example |
| P4 | Full flow demo: choose vehicle and SoC → top 3 with reasons → Nearest vs CERCOS comparison; p95 < 500 ms; e2e passes |
| Report | Format followed; ≥ 30 verified references; six contributions; synthetic results labelled |

## Final Phase-I check (before 10 Jan)
- [ ] `v1.0-phase1` tag on `main`; `docker compose up` works from a fresh clone
- [ ] Every member can explain their area for 3 minutes without notes and can name one limitation
- [ ] The report states what is real data and what is simulated
- [ ] Record book complete with weekly signatures
- [ ] Bonafide delivered; soft copy submitted via the Google Form
