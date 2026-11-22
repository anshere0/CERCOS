# KASHISH — Field Research: Census, Survey, Queue Observation & Analysis  (6% of the 40%)

**Mission:** collect the real-world data the whole project stands on, within 100 km of campus, ethically and with faculty approval, and turn it into weights and queue parameters (RQ2, RQ3, RQ4). Without your data, the engine is theory.
Your PRs are reviewed by **Eshwari** (primary) and **Atharva** (secondary, analysis scripts). You review **Eshwari** (primary) and **Eshwari's** data work; you also sanity-check that the field forms match the instruments.

## You own
`data/field/` (processed, anonymised files only) · `analysis/` (except `corridor_spacing_v0.py`, owned by Eshwari) · `docs/FIELD_PROTOCOL.md` · `docs/ETHICS.md` · the visit schedule

## Inputs / Outputs
| You need | From | When |
|---|---|---|
| Supervisor and faculty approval of the instruments | Faculty | W1 |
| Digital forms | Anshuman | 6 Dec (use Google Forms before that) |
| Field partners | All five others | per visit roster in `TEAM.md` |
| **You deliver** | | |
| Final instruments | Anshuman | **27 Nov** |
| Census file | Yash (import), Eshwari (corridor script) | batch 1 by 13 Dec, final 27 Dec |
| BWM weights, queue statistics | Atharva | **3 Jan** |
| Results summary + anonymised datasets | Eshwari (report) | 10 Jan |

## Task list by week
**W1 (23–29 Nov):** finalise the three instruments from `docs/FIELD_FORMS.md`. Survey = consent line, segment, vehicle, home charging, range-anxiety 1–5, Best-Worst over six criteria (**9 comparisons**), willingness to pay for zero wait. Write `docs/FIELD_PROTOCOL.md` and `docs/ETHICS.md` (consent text, no personal identifiers, equipment-only photos, storage and deletion). **Get faculty approval before any survey.** Create Google Form fallbacks. Book the first faculty-guided visit.
**W2:** pilot the survey with 3–5 people, fix wording; first census visit in Bhopal city.
**W3–W4:** census visits along the corridors (zones in `TEAM.md`); start the survey; make sure e-rickshaw drivers and e-2W riders are included, not only car owners.
**W5:** queue observation: ≥ 8 stations × 3 slots (07–10, 12–15, 18–21); keep the observation sheet identical across observers.
**W6:** finish fieldwork; clean data. Write `analysis/bwm_weights.py` (Best-Worst linear model solved with `scipy.optimize.linprog`; outputs weights, ξ and consistency ratio per respondent; group weights by geometric mean per segment), `analysis/queue_stats.py` (λ, μ, SCV per station and slot) and `analysis/survey_summary.py`.
**W7:** processed datasets into `data/field/processed/`; results summary for the report.

## Targets
**≥ 40 stations** (or every station that exists inside the zones, if fewer — say so) · **≥ 60 respondents** (target 20 per segment E2W / E3W / E4W) · **≥ 8 stations × 3 slots** observed.

## Commit trajectory
| Branch | Commits | PR title | Reviewer | Due |
|---|---|---|---|---|
| `docs/field-protocol-ethics` | `docs(field): add field protocol` → `docs(field): add ethics and consent text` → `docs(field): finalise instruments` | Protocol + ethics | Eshwari | 27 Nov |
| `data/census-batch-1` | `data(field): add anonymised census batch 1` | Census batch 1 | Eshwari | 13 Dec |
| `data/census-final` | `data(field): add census final batches` → `docs(field): census coverage notes` | Census final | Eshwari | 27 Dec |
| `data/survey-processed` | `data(field): add anonymised survey responses` | Survey data | Eshwari | 3 Jan |
| `data/queue-processed` | `data(field): add queue observations` | Queue data | Eshwari | 3 Jan |
| `feat/analysis-bwm` | `feat(analysis): add best-worst solver` → `test(analysis): published worked example` → `feat(analysis): group weights per segment` | BWM weights | Eshwari + Atharva | 3 Jan |
| `feat/analysis-queue` | `feat(analysis): queue statistics` → `feat(analysis): survey summary` | Queue stats + summary | Eshwari + Atharva | 3 Jan |
| `docs/field-results` | `docs(field): results summary for report` | Field results | Eshwari | 10 Jan |

## Definition of Done
- Faculty-approved instruments stored in the repo; consent text and ethics note exist.
- Counts met (or the shortfall is explained with reasons): stations, respondents per segment, queue observations.
- **No raw data, names, phone numbers or photos of people are in Git** (check `git log -p` for `data/field`).
- `bwm_weights.py` reproduces a published worked example; every segment has weights with a consistency measure.
- `queue_stats.py` outputs λ, μ, SCV for each observed station and time slot.
- Each visit is recorded in the record book with date, place, faculty initials and the pair.

## Antigravity prompt (Planning mode, branch `feat/analysis-bwm`)
```
Read AGENTS.md, docs/FIELD_FORMS.md, docs/ETHICS.md and contracts/schema.sql (survey_responses).
You work for Kashish. Edit ONLY analysis/ (except corridor_spacing_v0.py), data/field/processed/, docs/FIELD_PROTOCOL.md, docs/ETHICS.md.
Task: implement analysis/bwm_weights.py using the linear Best-Worst Method: minimise xi subject to |w_B - a_Bj*w_j| <= xi and |w_j - a_jW*w_W| <= xi for all j, sum(w)=1, w>=0, solved with scipy.optimize.linprog. Input: anonymised survey CSV; output per-respondent weights and consistency ratio, plus group weights per segment by geometric mean with bootstrap confidence intervals. Add a test using a published worked example.
Never read or write data/field/raw/ into Git. Plan first, small commits as in docs/team/kashish.md. Do not push to main.
```

## Rules specific to you
- **Do not start a survey without faculty approval.** Fix any concern before the first respondent.
- Raw files stay on a shared drive with a backup; only anonymised processed files are committed.
- Ask for permission at every station; never touch equipment; never photograph people.
- Do not skip the e-rickshaw and e-2W groups to finish faster.

## Report evidence (your half page)
Protocol, sample sizes, ethics measures, the visit log, the weights per segment with consistency, and limitations such as sample bias.
