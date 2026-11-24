# CERCOS Field Research Instruments & Survey Architecture
**Lead:** Kashish (Field Research Lead)  
**Consumer:** Anshuman (Frontend Form Builder) & Yash (Database Seed Engineer)  
**Programme:** EPICS Phase-I, VIT Bhopal University  
**Status:** Final Specification for Field Data Collection  

---

## 1. Instrument 1: Charging Station Census Specification

One record is completed per visited charging station facility. Connector details map 1-to-many into the connectors table.

| Field Name | Enumerator Prompt / Question | Data Type | Permitted Values / Constraints | Req? | Database Column Mapping (`contracts/schema.sql`) | Mapping Status & Notes |
|---|---|---|---|:---:|---|---|
| `station_name` | Name of station or location descriptor | `VARCHAR(150)` | Free text (e.g. *"Tata Power - MP Nagar Zone 1"*) | Yes | `cercos.charging_stations.station_name` | Direct match |
| `cpo_name` | Charge Point Operator / Network Brand | `VARCHAR(100)` | `Tata Power`, `Statiq`, `Jio-bp`, `ChargeZone`, `MPPKVVCL`, `Ather`, `Other` | Yes | `cercos.charging_stations.cpo_name` | Direct match |
| `district_name` | Administrative district | `VARCHAR(100)` | `Bhopal`, `Sehore`, `Vidisha`, `Raisen`, `Narmadapuram` | Yes | `cercos.districts.district_name` | Maps via FK `district_id` |
| `address` | Street address or landmark description | `TEXT` | Free text | Yes | `cercos.charging_stations.address` | Direct match |
| `latitude` | GPS Latitude (decimal degrees) | `NUMERIC(9,6)` | $22.500000$ to $23.900000$ | Yes | `cercos.charging_stations.geom` (`Point`) | Combined into PostGIS geometry |
| `longitude` | GPS Longitude (decimal degrees) | `NUMERIC(9,6)` | $76.800000$ to $78.200000$ | Yes | `cercos.charging_stations.geom` (`Point`) | Combined into PostGIS geometry |
| `is_operational` | Is the station actively powered & functional? | `BOOLEAN` | `true`, `false` | Yes | `cercos.charging_stations.is_operational` | Direct match |
| `open_24x7` | Is the station accessible 24 hours daily? | `BOOLEAN` | `true`, `false` | Yes | `cercos.charging_stations.open_24x7` | Direct match |
| `hours_text` | Operating hours if not 24x7 | `VARCHAR(100)` | Text (e.g. *"06:00 - 22:00"*) or `24x7` | No | `cercos.charging_stations.hours_text` | Direct match |
| `tariff_inr_kwh` | Published electricity tariff per kWh | `NUMERIC(5,2)` | Positive float (e.g. `14.50`) | Yes | `cercos.charging_stations.tariff_inr_kwh` | Direct match |
| `rating` | Observed general quality & facility rating | `NUMERIC(2,1)` | $1.0$ to $5.0$ | No | `cercos.charging_stations.rating` | Direct match |
| `connector_type` | Physical plug type on charger | `VARCHAR(30)` | `CCS2`, `Type2`, `Bharat_DC001`, `Bharat_AC001`, `LECCS`, `GBT`, `SWAP` | Yes | `cercos.connectors.connector_type` | Direct match in child table |
| `output_power_kw` | Maximum rated power output per gun | `NUMERIC(6,2)` | Float $> 0$ (e.g. `3.3`, `7.4`, `30.0`, `60.0`) | Yes | `cercos.connectors.output_power_kw` | Direct match in child table |
| `connector_status`| Status of individual plug | `VARCHAR(20)` | `AVAILABLE`, `OCCUPIED`, `FAULTY`, `OFFLINE`, `UNKNOWN` | Yes | `cercos.connectors.status` | Direct match in child table |
| `payment_methods`| Supported payment methods | `VARCHAR(60)` | `RFID`, `App_UPI`, `Credit_Debit`, `Cash` | No | *(None in schema)* | **Issue for Yash:** Store in `source_ref` or add column |
| `app_required` | Proprietary CPO app mandatory to start session? | `BOOLEAN` | `true`, `false` | Yes | *(None in schema)* | **Issue for Yash:** Store in `source_ref` or add column |
| `enumerator` | Full name of visiting student researcher | `VARCHAR(40)` | Name from team roster | Yes | `cercos.charging_stations.source_ref` | Logged as metadata |

---

## 2. Instrument 2: Driver Survey & Best-Worst Method (BWM)

Administered verbally to drivers of E2W, E3W, and E4W vehicles.

### Section A: Demographics & Charging Background
| Field Name | Question Wording (English & Hindi) | Data Type | Permitted Values | Database Column (`contracts/schema.sql`) | Mapping Status |
|---|---|---|---|---|---|
| `consent` | *"Do you agree to participate?"* / *"क्या आप इस सर्वे में भाग लेने के लिए सहमत हैं?"* | `BOOLEAN` | `true` (Mandatory: survey aborts if false) | `cercos.survey_responses.consent` | Direct match (`CHECK (consent = TRUE)`) |
| `segment` | *"Vehicle type"* / *"वाहन का प्रकार"* | `VARCHAR(10)` | `E2W`, `E3W`, `E4W`, `ELCV` | `cercos.survey_responses.segment` | Direct match |
| `vehicle_model`| *"Vehicle make and model"* / *"गाड़ी का मॉडल"* | `VARCHAR(100)` | e.g. *"Mahindra Treo"*, *"Ola S1"*, *"Tata Nexon EV"* | `cercos.survey_responses.vehicle_model` | Direct match |
| `area` | *"General area of daily operation / route"* / *"संचालन का मुख्य क्षेत्र"* | `VARCHAR(60)` | e.g. *"Bhopal Local"*, *"Bhopal-Sehore Highway"* | `cercos.survey_responses.area` | Direct match |
| `home_charging`| *"Do you have a dedicated charger at home/depot?"* / *"क्या आपके घर या गैराज में चार्जर उपलब्ध है?"* | `BOOLEAN` | `true`, `false` | `cercos.survey_responses.home_charging` | Direct match |
| `range_anxiety`| *"How anxious are you about running out of battery?"* (1=Not anxious, 5=Extremely anxious) / *"बैटरी खत्म होने की कितनी चिंता रहती है?"* (1-5) | `SMALLINT` | `1`, `2`, `3`, `4`, `5` | `cercos.survey_responses.range_anxiety` | Direct match (`CHECK BETWEEN 1 AND 5`) |

### Section B: Best-Worst Method (BWM) Criteria Evaluation (9 Comparisons)
The evaluation covers 6 critical charging decision attributes:
1. **Detour Distance** ($C_1$): Extra kilometers driven away from route.
2. **Charging Cost** ($C_2$): Electricity tariff per unit (INR/kWh).
3. **Queue Wait Time** ($C_3$): Time spent waiting in line for a charger.
4. **Charging Speed** ($C_4$): Charger power rating (fast vs slow charging).
5. **Station Rating** ($C_5$): Reliability, cleanliness, safety, amenities.
6. **Battery Safety** ($C_6$): Slow/steady charging to preserve battery lifespan.

#### Protocol:
- **Step 1 (Select Best):** Respondent chooses the **Single Most Important** criterion $\rightarrow$ stored in `best_criterion` (`VARCHAR(20)`).
- **Step 2 (Select Worst):** Respondent chooses the **Single Least Important** criterion $\rightarrow$ stored in `worst_criterion` (`VARCHAR(20)`).
- **Step 3 (Best-to-Others Ratings):** Respondent rates how much more important the **Best criterion** is compared to each of the remaining 5 criteria on a scale of $1$ (Equally important) to $9$ (Extremely more important).
  $\rightarrow$ Stored as JSONB in `best_to_others`: `{"detour": 3, "cost": 1, "wait": 5, "speed": 4, "rating": 7, "battery": 6}`.
- **Step 4 (Others-to-Worst Ratings):** Respondent rates how much more important each of the remaining 4 criteria is compared to the **Worst criterion** on a scale of $1$ to $9$.
  $\rightarrow$ Stored as JSONB in `others_to_worst`: `{"detour": 5, "cost": 8, "wait": 4, "speed": 5, "battery": 2}`.
  *(Note: Exactly $5 + 4 = 9$ distinct, non-redundant pairwise comparisons).*

### Section C: Economic Valuation
| Field Name | Question Wording (English & Hindi) | Data Type | Permitted Values | Database Column | Mapping Status |
|---|---|---|---|---|---|
| `wtp_zero_wait_inr` | *"How much extra per kWh would you pay to skip the queue and charge immediately?"* / *"अगर लाइन में बिना खड़े तुरंत चार्जिंग मिले, तो आप प्रति यूनिट कितने रुपये अतिरिक्त दे सकते हैं?"* | `NUMERIC(6,2)` | Float $\ge 0$ (e.g. `0.00`, `2.50`, `5.00`) | `cercos.survey_responses.wtp_zero_wait_inr` | Direct match |
| `enumerator` | Student interviewer name | `VARCHAR(40)` | Name from roster | `cercos.survey_responses.enumerator` | Direct match |

---

## 3. Instrument 3: Station Queue & Occupancy Observation Sheet

Recorded at selected hubs in consecutive 15-minute intervals across 3-hour observation windows (`07:00–10:00`, `12:00–15:00`, `18:00–21:00`).

| Field Name | Description | Data Type | Permitted Values | Database Column (`contracts/schema.sql`) | Mapping Status |
|---|---|---|---|---|---|
| `station_id` | Foreign key referencing charging station | `INT` | Valid `cercos.charging_stations.station_id` | `cercos.station_observations.station_id` | Direct match |
| `observed_at` | Date and start timestamp of 15-min interval | `TIMESTAMPTZ` | Timestamp | `cercos.station_observations.observed_at` | Direct match |
| `slot` | Designated diurnal observation window | `VARCHAR(10)` | `07-10`, `12-15`, `18-21` | `cercos.station_observations.slot` | Direct match (`CHECK IN (...)`) |
| `vehicles_waiting` | Vehicles physically queuing in line | `SMALLINT` | Integer $\ge 0$ | `cercos.station_observations.vehicles_waiting` | Direct match |
| `connectors_busy` | Connectors actively plugged into vehicles | `SMALLINT` | Integer $\ge 0$ | `cercos.station_observations.connectors_busy` | Direct match |
| `arrivals_in_interval` | New vehicles arriving to charge during the 15 mins | `SMALLINT` | Integer $\ge 0$ | `cercos.station_observations.arrivals_in_interval` | Direct match |
| `interval_minutes` | Duration of observation slice | `SMALLINT` | Default `15` | `cercos.station_observations.interval_minutes` | Direct match |
| `session_start` | Timestamp vehicle initiated charging | `TIMESTAMPTZ` | Timestamp (for tracked sessions) | `cercos.station_observations.session_start` | Direct match |
| `session_end` | Timestamp vehicle disconnected | `TIMESTAMPTZ` | Timestamp (for tracked sessions) | `cercos.station_observations.session_end` | Direct match |
| `kwh_delivered` | Total energy delivered during session | `NUMERIC(6,2)` | Float $\ge 0$ | `cercos.station_observations.kwh_delivered` | Direct match |
| `observer` | Name of observing team member | `VARCHAR(40)` | Name from roster | `cercos.station_observations.observer` | Direct match |

---

## 4. Google Forms Interim Build Sheet (Until Frontend Field Mode Ships)

The team uses Google Forms for field entry during Weeks 1–3 before Anshuman's web forms are online:

1. **Form 1: Station Census Form**
   - Section 1: Facility Identifiers (Name, Operator, Address, District dropdown).
   - Section 2: Location (Latitude, Longitude via Google location link or manual GPS).
   - Section 3: Hardware (Connector Type checkboxes, Rated kW, Plugs count).
   - Section 4: Operational Data (Working status, 24x7, Tariff INR/kWh, Payment modes).
   - Section 5: Verification (Equipment photo upload, Enumerator name).
2. **Form 2: Driver Survey Form**
   - Section 1: Informed Consent Checkbox (Required = TRUE, otherwise submit breaks).
   - Section 2: Vehicle Profile (Segment: E2W, E3W, E4W; Model name; Area).
   - Section 3: Charging Routine & Range Anxiety (Likert 1 to 5).
   - Section 4: BWM Best & Worst Selection (Dropdown of 6 criteria).
   - Section 5: Best-to-Others Rating (Linear scale 1 to 9 for remaining 5 criteria).
   - Section 6: Others-to-Worst Rating (Linear scale 1 to 9 for remaining 4 criteria).
   - Section 7: Willingness-to-Pay (Short answer number).
3. **Form 3: Queue Observation Sheet**
   - Section 1: Station Selector & Slot dropdown (`07-10`, `12-15`, `18-21`).
   - Section 2: Interval Log (Time stamp, Vehicles in queue, Guns busy, New arrivals).

---

## 5. Handoff Specification to Anshuman (Frontend UI Developer)

Anshuman, when developing the React `/field` mobile forms:
- Form components must enforce validation matching the permitted values above.
- The BWM component requires a dynamic UI:
  - Step 1 renders 6 cards to select `best_criterion`.
  - Step 2 disables the selected best and renders 5 cards to select `worst_criterion`.
  - Step 3 generates 5 slider/stepper rows (scale 1 to 9) comparing Best $\rightarrow$ others.
  - Step 4 generates 4 slider/stepper rows (scale 1 to 9) comparing others $\rightarrow$ Worst.
- Must support **Offline Mode**: cache filled submissions in `localStorage` or IndexedDB and push to API upon regaining connectivity.
