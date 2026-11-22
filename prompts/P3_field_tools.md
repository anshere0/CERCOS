# P3 — Field-research tooling (supports the EPICS fieldwork)
Build an admin-only "Field Mode" (mobile-first PWA pages) to capture, offline-tolerant:
(a) Station census form (name, operator, GPS, connectors, kW, posted tariff, hours, photo, working? y/n, enumerator, timestamp);
(b) User survey (vehicle segment/model, typical trip, home charging yes/no, range-anxiety scale 1-5, and the Best-Worst
    comparison tasks for the 6 criteria, 9 comparisons per respondent, consent checkbox, no personal identifiers);
(c) Queue observation sheet (station, time slot, vehicles waiting, connectors busy, session start/end timestamps).
Backend: endpoints + validation; CSV export; `analysis/bwm_weights.py` (Best-Worst Method -> weights per segment) and
`analysis/ahp_weights.py`. Include consent text and a data-protection note in docs/ETHICS.md.
Acceptance: forms work on a phone viewport; export opens in Excel; BWM script reproduces a published worked example.

Also add `analysis/corridor_spacing_v0.py`: snap census stations to a corridor polyline, list inter-station spacing, flag > 25 km (MoP norm) and > 100 km without a fast charger; output CSV + simple chart.
