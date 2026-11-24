# CERCOS Field Research Protocol
**Lead:** Kashish (Field Research Lead)  
**Programme:** EPICS Phase-I, VIT Bhopal University  
**Scope:** Study area within 100 km radius of VIT Bhopal campus  
**Status:** Working Protocol for Team Field Visits  

---

## 1. Study Area and Geographic Zones

Field investigation is conducted across four designated zones spanning urban, peri-urban, and inter-city highway corridors in the Bhopal capital region:

| Zone | Corridor / Region | Key Road Links | Primary Characteristics | Target Stations |
|---|---|---|---|:---:|
| **Zone 1** | **Bhopal City Core** | MP Nagar, Kolar, Hoshangabad Rd, Arera Colony | Dense commercial, high e-2W/e-3W volume | 15–20 |
| **Zone 2** | **Bhopal – Sehore – Ashta** | SH-18 / NH-46 (Indore direction) | Heavy inter-city transit, freight, tier-3 hubs | 8–12 |
| **Zone 3** | **Bhopal – Vidisha – Sanchi** | SH-19 (Heritage & agricultural corridor) | Mixed rural-urban, highway dhabas | 6–8 |
| **Zone 4** | **Bhopal – Narmadapuram – Raisen** | NH-46 / SH-22 (South-East corridor) | River basin transit, industrial outposts | 8–10 |

---

## 2. Field Visit Roster (Two-Person Pairs)

All visits are conducted in pairs for personal safety, data cross-verification, and adherence to university field guidelines:

| Corridor / Zone | Round 1 Pair | Round 2 Pair | Round 3 Pair |
|---|---|---|---|
| **Bhopal City Core** | Kashish + Anshuman (Pair A) | Eshwari + Yash (Pair B) | Atharva + Ansh (Pair C) |
| **Bhopal – Sehore – Ashta** | Eshwari + Yash (Pair B) | Atharva + Ansh (Pair C) | Kashish + Anshuman (Pair A) |
| **Bhopal – Vidisha – Sanchi** | Atharva + Ansh (Pair C) | Kashish + Anshuman (Pair A) | Eshwari + Yash (Pair B) |
| **Bhopal – Narmadapuram – Raisen** | Kashish + Anshuman (Pair A) | Eshwari + Yash (Pair B) | Atharva + Ansh (Pair C) |

*Schedule coordination is managed by Kashish. Each pair is responsible for completing and logging their assigned visits.*

---

## 3. Step-by-Step Station Visit Procedure

### Phase A: Pre-Departure Preparation
1. Verify device battery, install offline forms (or Google Forms caching), and carry physical printed fallback forms.
2. Ensure both team members wear their official VIT Bhopal student identity cards.
3. Carry the signed Faculty Supervisor Permission Letter and Information Sheet.
4. Verify transport, emergency contact numbers, and drinking water.

### Phase B: On-Site Arrival & Courtesy Protocol
1. Approach station supervisor, attendant, or commercial operator immediately upon arrival.
2. Introduce yourselves: *"We are undergraduate engineering students from VIT Bhopal conducting an academic research project on EV charging accessibility under the EPICS curriculum."*
3. Present the faculty authorization letter. Request polite verbal permission to inspect charger specifications and survey drivers.
4. If permission is denied or staff is hostile, do not argue. Record the station as `ACCESS_RESTRICTED` in notes and leave immediately.

### Phase C: Charging Station Census Logging
1. Record exact GPS latitude and longitude coordinates using mobile GPS averaging (min. 10 satellites, accuracy $< 5\text{ m}$).
2. Inspect charger nameplates and display screens:
   - CPO / Operator brand (e.g., Tata Power, Statiq, Jio-bp, ChargeZone, MP Discom).
   - Connector types present (`CCS2`, `Type-2 AC`, `Bharat DC-001`, `Bharat AC-001`, `LECCS`).
   - Rated power per gun (kW).
   - Operational status (`ONLINE_OPERATIONAL`, `OFFLINE`, `HARDWARE_FAULT`, `UNDER_MAINTENANCE`).
3. Document published tariffs (INR/kWh or INR/minute) from tariff boards or mobile app screens.
4. Photograph equipment nameplate and tariff board ONLY. **Zero faces or vehicle number plates in photos.**

### Phase D: Driver Behavioral Survey
1. Approach EV drivers while their vehicle is actively charging or waiting in queue.
2. **Never approach drivers during active plug-in, high-voltage cable maneuvering, or emergency situations.**
3. Read the verbal Informed Consent script (`docs/ETHICS.md`) in English or Hindi.
4. If driver consents, administer the 5-minute structured survey:
   - Vehicle class (E2W, E3W, E4W) and model.
   - Home charging access and charging habits.
   - Range anxiety rating (1 to 5).
   - **Best-Worst Criteria Evaluation (9 comparisons):** Guide driver to pick their Most Important and Least Important factors, then rate the remaining criteria against them.
   - Willingness to pay for zero wait time.
5. Thank the driver for their contribution to regional mobility research.

### Phase E: Queue & Occupancy Observation
1. Stand or sit in a safe, non-obstructive vantage point with a clear view of the charging bays.
2. Conduct observations in structured 15-minute intervals across the assigned time slot (`07:00–10:00`, `12:00–15:00`, or `18:00–21:00`).
3. At the end of every 15-minute interval, log:
   - Number of vehicles plugged in and drawing charge.
   - Number of vehicles waiting in queue.
   - Number of new vehicle arrivals during the interval.
   - Session duration (start time, end time, kWh delivered if displayed).

---

## 4. Strict Safety & Ethical Ground Rules

1. **High-Voltage Safety:** Never touch charging connectors, power cabinets, cables, transformers, or live electrical infrastructure. Keep a safe distance ($\ge 1\text{ m}$) from active high-power DC fast-chargers.
2. **Privacy Protection:** Never photograph drivers, passengers, attendants, or vehicle registration plates. If an accidental photo contains a person or license plate, delete it immediately.
3. **No Coercion:** Participation is 100% voluntary. Never pressure a driver or offer financial incentives.
4. **Segment Quota Balance:** Field researchers must deliberately seek out commercial e-rickshaw (E3W) drivers and daily commuter scooter (E2W) riders at local charging hubs, avoiding the bias of surveying only luxury passenger car owners.

---

## 5. Quantitative Field Targets (Phase-I Minimums)

- **Station Census:** $\ge 40$ charging stations (or total census of all physical public charging points in the 4 corridors).
- **User Survey Sample:** $\ge 60$ completed responses with balanced representation:
  - $\ge 20$ E2W (Two-wheelers)
  - $\ge 20$ E3W (Three-wheelers / E-rickshaws)
  - $\ge 20$ E4W (Four-wheelers / Cabs / Private cars)
- **Queue Observations:** $\ge 8$ stations observed across all 3 time slots ($8 \times 3 = 24$ observation blocks).

---

## 6. Data Custody and Anonymization Workflow

1. Raw physical questionnaires and field notes are photographed and uploaded to the secure team Google Drive (`/raw_field_data/`), accessible only to the 6 team members.
2. Raw data is transcribed into CSV by Kashish. All identifying notes are stripped.
3. Every data row is assigned an anonymous surrogate key (`response_id`, `station_id`).
4. **Only sanitized, fully anonymized CSV files are committed to Git** inside `data/field/processed/`.
5. Raw media, photos, and identifiable audio recordings are strictly excluded from Git via `.gitignore` (`data/field/raw/`, `data/field/photos/`).

---

## 7. Faculty Record-Book Template

After every field outing, the team pair must record the visit in their physical EPICS log book and obtain faculty supervisor initials:

```text
Date: [DD/MM/YYYY]
Zone: [e.g., Zone 2: Bhopal–Sehore Highway]
Pair: [e.g., Kashish & Anshuman]
Time Window: [e.g., 08:30 – 13:00]
Stations Visited (Names & CPOs): 
  1. Tata Power - Sehore Bypass (Operational, 2x CCS2)
  2. Statiq - Ashta Highway Hub (Offline, 1x CCS2)
Surveys Completed: [e.g., 4 E2W, 3 E3W, 2 E4W]
Queue Sessions Observed: [e.g., 1 slot (07-10) at Sehore Hub]
Supervisor Verification Initials: [ _______________ ]
```
