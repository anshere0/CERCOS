# CERCOS Data Sources & Macro Ingestion Protocol
**Lead:** Eshwari (Draft) · **Finalizer / Consumer:** Yash (ETL Pipeline Lead)  
**Programme:** EPICS Phase-I, VIT Bhopal University  
**Status:** Ingestion Guide & License Auditing Document  

---

## 1. Registry of Project Datasets

| Dataset | Primary Source | Extraction Method | License / Terms of Use | Update Frequency | Target Storage Location |
|---|---|---|---|---|---|
| **MP District EV Registrations** | MoRTH VAHAN 4.0 Dashboard (`vahan.parivahan.gov.in`) | Manual public analytics dashboard export | Government of India Open Data / Fair Academic Use | Monthly | `data/vahan/mp_district_ev_*.csv` |
| **Official MP Charging Station Census** | Ministry of Heavy Industries (MHI), Rajya Sabha Unstarred Q 3910 (27 Mar 2026) | Parliamentary official PDF annexure | Government of India Open Public Record | Snapshot (1 Mar 2026) | `docs/MHI_RS_Q3910_MP_Stations.pdf` |
| **Crowdsourced Station Points** | OpenStreetMap (OSM) via Overpass API | Overpass automated API queries | Open Database License (ODbL 1.0) | Automated ingest (Yash) | `data/osm/` |
| **Open Charge Map (OCM)** | Open Charge Map API (`openchargemap.org`) | REST API batch client | Creative Commons Attribution-ShareAlike 4.0 | Periodic API pull | `data/ocm/` |
| **Empirical Station Census** | CERCOS On-Ground Field Visits (Bhopal & Corridors) | In-person mobile observation (`FIELD_FORMS.md`) | CERCOS Team Open Research Dataset | Phase-I primary data | `data/field/processed/census.csv` |
| **User BWM Survey** | Driver Interviews across 4 Corridors | Verbal interview with informed consent | CERCOS Team Anonymized Research Data | Phase-I primary data | `data/field/processed/survey_responses.csv` |

---

## 2. Step-by-Step VAHAN Dashboard Manual Export Procedure

*This procedure documents the manual extraction of district-level EV registration metrics without scraping.*

1. **Access Portal:** Navigate to the public analytics portal: `https://vahan.parivahan.gov.in/vahan4dashboard/`.
2. **Set Geographic Filter:**
   - On the left sidebar filter, select **State:** `Madhya Pradesh`.
   - Leave **RTO:** `All RTOs` (to capture statewide district breakdown).
3. **Set Temporal Range:**
   - Select **Year:** `2024` (and sequentially export `2019`, `2020`, `2021`, `2022`, `2023` for historical adoption trend modeling).
4. **Select Category Cross-Tabulation:**
   - Under the primary table view, select **Y-Axis (Rows):** `District / RTO Name`.
   - Select **X-Axis (Columns):** `Fuel Type` (ensuring `ELECTRIC(BOV)`, `PETROL`, `DIESEL`, `CNG` are shown).
   - Under vehicle class breakdown, filter by:
     - `TWO WHEELER(NT)` + `TWO WHEELER(T)`
     - `THREE WHEELER(T)` (Passenger & Cargo)
     - `MOTOR CAR(LMV)` (Four-wheelers)
5. **Export File:**
   - Click the green **Export to Excel / CSV** button located at the top-right of the results matrix.
   - Save the raw download as `data/vahan/raw/vahan_mp_2024_fuel_district.xlsx`.
6. **Data Cleaning & Standardization:**
   - Standardize column names to: `district_name, rto_code, ev_total, ev_e2w, ev_e3w, ev_e4w, ev_other, year`.
   - Ensure district names match official census spelling in `cercos.districts` (e.g., `Bhopal`, `Sehore`, `Vidisha`, `Raisen`, `Narmadapuram`).
   - Save sanitized file to: `data/vahan/mp_district_ev_cleaned.csv`.

---

## 3. Official Parliamentary Baseline Data (MHI Rajya Sabha Q 3910)

According to the official written answer provided by the Minister of State for Heavy Industries on **27 March 2026** to Rajya Sabha Unstarred Question No. 3910:
- **Total Public Charging Stations Installed by OMCs in Madhya Pradesh:** **1,417**
- **Total Public Charging Stations Fully Operational in Madhya Pradesh:** **1,291**
- **Operational Efficiency Ratio:** $\frac{1291}{1417} \approx 91.1\%$
- **Key Parliamentary Finding:** The Ministry noted that *no centralized statewide repository tracks real-time charger availability, live connector telemetry, or highway corridor spacing compliance (25 km spacing norm)*. This directly validates the community and academic necessity of the CERCOS project.
