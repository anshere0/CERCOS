# Member Contribution Report — Eshwari

**Role:** Literature Review, Policy & VAHAN Empirical Data, Corridor Gap Analytics & Phase-I Report Lead  
**Phase-I Allocation:** 5% of Total Project (40% Phase-I Scope)  
**Primary Owned Paths:** `docs/LITERATURE.md`, `docs/references.bib`, `data/policy/`, `data/vahan/`, `analysis/corridor_spacing_v0.py`, `docs/PHASE_I_REPORT_DRAFT.md`, `docs/CERCOS_Phase_I_Report.docx`, `docs/EXCLUSIVE_RESEARCH_REPORT.md`

---

## 1. Key Deliverables Completed

1. **Verified Literature Survey & Bibliography (`docs/LITERATURE.md`, `docs/references.bib`)**
   - Compiled comparative literature synthesis across EV charging routing, MCDM methods (TOPSIS / BWM rank-reversal sensitivity), spatial accessibility (2SFCA), and non-telemetry queueing models.
   - Curated verified BibTeX references in `docs/references.bib` paired with strict citation verification tracking (`docs/references_unverified.md`).

2. **Official Policy & VAHAN Empirical Benchmarks (`data/policy/`, `data/vahan/`)**
   - Compiled verifiable Indian EV registries and policy baselines used across the backend status API and research report:
     - **MoRTH VAHAN 4.0 (CY 2024 MP):** `62,597` new EVs (`49.61%` E2W, `47.57%` E3W, `2.37%` E4W, `0.45%` heavy/bus) establishing the 97.18% light-EV fleet dominance.
     - **MHI Rajya Sabha Unstarred Q.3910 (27 Mar 2026):** `1,417` OMC stations installed / `1,291` operational in MP (`91.11%`), noting absence of centralized spatial gap tracking.
     - **Ministry of Power (MoP 2022) & MPERC Tariff Orders:** `25 km` highway norm, `3x3 km` urban grid norm, `100 km` heavy-duty fast charger norm, and `₹6.8–8.2/kWh` regulated DISCOM base tariffs.

3. **NH-46 Highway Corridor Spacing Audit (`analysis/corridor_spacing_v0.py`)**
   - Implemented spatial projection script snapping stations onto the Bhopal – Sehore – Kothri Kalan – Ashta – Dewas – Indore corridor polyline and flagging stretches exceeding MoP's `> 25 km` spacing threshold and `> 100 km` fast-charger gaps.
   - Analyzed real ingested MP station data (`274` corridor-proximate stations out of `508`, max gap `21.31 km` along the trunk) and generated `analysis/corridor_spacing_report.csv` + `analysis/corridor_spacing_chart.png`.

4. **Phase-I Project Report Assembly (`docs/PHASE_I_REPORT_DRAFT.md`, `docs/CERCOS_Phase_I_Report.docx`)**
   - Integrated all empirical data sources, figures (`research/figures/`), architecture diagrams, and team sections into the formatted Phase-I Word/Markdown submission package (`PR #5`, `PR #6`).

---

## 2. Pull Requests & Verification Evidence
- **Merged PRs:** PR `#4` (`docs/literature-start`), PR `#5` (`feat/research-fleet-experiment`), PR `#6` (`docs/phase-1-report`).
- **Verification Status:** `test_corridor_spacing_flags_gaps_over_25km` passing in pytest (`74/74`), and `research/01_cercos_pilot_experiments.py` passing cleanly in CI (`research-script` job).
