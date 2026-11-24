# CERCOS Systematic Literature Review & Comparative Analysis
**Lead:** Eshwari (Literature, Policy & Report Lead)  
**Programme:** EPICS Phase-I, VIT Bhopal University  
**Status:** Working Corpus & Analytical Comparison Table  

---

## 1. Thematic Comparative Analysis Table

This table maps existing literature across six foundational research domains. For each entry, the specific methodology, vehicle segments covered, evaluation criteria, empirical data grounding, and critical limitations (*"What it misses"*) are detailed based on verified abstracts and publications.

| Citation | Domain | Methodology | Vehicles Covered | Criteria Evaluated | Empirical Data Used | What It Misses (Critical Gap) | Source Read |
|---|---|---|---|---|---|---|:---:|
| **Hwang & Yoon (1981)** | MCDM | Classical TOPSIS (Euclidean distance to ideal & anti-ideal) | Generic | Cost, Benefit attributes | Synthetic numerical examples | Dynamic candidate sets trigger rank reversal when alternatives are added/removed. | Full text |
| **Behzadian et al. (2012)** | MCDM | Systematic survey of 266 TOPSIS applications across sectors | Generic | Multi-attribute decision criteria | Literature database (1981–2011) | Does not address real-time routing or spatial coordinate constraints. | Full text |
| **Garcia-Cascales & Lamata (2012)** | MCDM | Rank-reversal analysis in TOPSIS normalization | Generic | Vector vs linear scale normalization | Mathematical proofs & test matrices | Focuses on theoretical matrix transformations; lacks domain application to charging queues. | Full text |
| **Wang & Luo (2009)** | MCDM | Invariance analysis of decision criteria under alternative addition | Generic | Relative weight distribution | Algorithmic test cases | Identifies rank reversal causes but does not propose anchored criteria boundaries for spatial routing. | Full text |
| **Rezaei (2015)** | MCDM | Best-Worst Method (BWM) linear programming formulation | Generic | Multi-criteria pairwise ratings ($2n-3$) | Practical case studies | Static survey method; requires integration with downstream spatial MCDM engines. | Full text |
| **Diakoulaki et al. (1995)** | MCDM | CRITIC method (objective weighting via correlation & std dev) | Generic | Contrast intensity & conflict | Economic corporate data | Purely objective weighting; fails to capture heterogeneous driver preferences (e.g., e-rickshaws vs cars). | Full text |
| **Schneider et al. (2014)** | Routing | Electric Vehicle Routing Problem with Time Windows (E-VRPTW) | E4W Commercial Fleet | Distance, time windows, battery capacity | Benchmark routing graphs | Assumes linear battery recharge rates; ignores charging station queues and real accepted kW bottlenecks. | Full text |
| **Franke et al. (2012)** | Range Anxiety | Longitudinal psychological analysis of EV range utilization | E4W Passenger Cars (MINI E) | Comfortable Range Buffer (CRB), Battery SoC | 6-month field trial ($n=40$ drivers) | Studied high-income European passenger car drivers; completely inapplicable to Indian 2W/3W commercial realities. | Full text |
| **Rauh et al. (2015)** | Range Anxiety | Empirical study of driver experience vs. range anxiety reduction | E4W Passenger Cars | Range anxiety scale, odometer mileage | Field study across experienced vs novice EV drivers | Does not model multi-criteria charging stop decision making under critical low-SoC thresholds. | Abstract only |
| **Rezvani et al. (2015)** | Adoption | Consumer EV adoption framework review | E4W Cars | Total cost of ownership, range, charging availability | Systematic literature synthesis | Excludes light commercial vehicles (LCVs) and electric three-wheelers (E3Ws). | Abstract only |
| **Church & ReVelle (1974)** | Siting | Maximal Covering Location Problem (MCLP) | Facility Location | Geometric coverage distance ($S$) | Synthetic spatial networks | Binary coverage assumption (point is either covered or uncovered); ignores highway transit corridors. | Full text |
| **Hodgson (1990)** | Siting | Flow-Capturing Location-Allocation Model (FCLM) | Transit Traffic | Origin-destination path flows | Network centroid matrices | Treats vehicles as passing through; fails to account for onboard battery discharge along the path. | Full text |
| **Kuby & Lim (2005)** | Siting | Flow-Refueling Location Model (FRLM) | Alternative Fuel / EV | Vehicle range ($R$), station spacing | Highway network graphs | Assumes single fuel-type and unlimited capacity per station; ignores queuing bottlenecks. | Full text |
| **Luo & Wang (2003)** | Accessibility | Two-Step Floating Catchment Area (2SFCA) method | Spatial Services | Provider-to-population ratio, travel thresholds | Chicago metropolitan GIS data | Static threshold distances; does not capture real-time dynamic charger availability. | Full text |
| **Anselin (1995)** | Spatial Stats | Local Indicators of Spatial Association (LISA) | Spatial Demographics | Local Moran's $I$, spatial lag | US census economic data | Spatial clustering metric; does not evaluate regulatory statutory norms (e.g., MoP 3x3 km grid). | Full text |
| **Kleinrock (1975)** | Queuing | M/M/1 and M/M/c Markovian queueing system fundamentals | Stochastic Service | Arrival rate ($\lambda$), service rate ($\mu$), wait time ($W$) | Telecommunication data | Assumes exponential service times, whereas EV charging is deterministic/state-of-charge dependent. | Full text |
| **Gross et al. (2008)** | Queuing | Erlang-C waiting probability in multi-server systems | Service Systems | Server utilization ($\rho$), queue length ($L_q$) | Standard queueing benchmarks | Lacks approximation for non-Poisson arrivals with high variance (SCV $\neq 1$). | Full text |
| **Allen (1978)** | Queuing | Allen-Cunneen approximation formula for general M/G/c queues | Multi-server queues | Mean wait time $W_q$, arrival/service SCV | Computing systems benchmarks | Theoretical approximation; requires empirical field calibration of $\lambda$ and $\mu$ for EV chargers. | Full text |
| **Lee et al. (2019)** | Charging Data | ACN-Data: Public dataset of EV workplace charging sessions | E4W Passenger Cars | Energy delivered (kWh), session duration, charging rate | Caltech adaptive charging network ($>30,000$ sessions) | Captures privileged US workplace depot charging; entirely different operational dynamics than Indian roadside fast hubs. | Full text |
| **Luxen & Vetter (2011)** | Spatial Routing | Real-time shortest path routing via Contraction Hierarchies (OSRM) | Road Vehicles | Metric distance, road hierarchy | OpenStreetMap European network | Optimizes geometric travel time; does not compute multi-criteria charging utility stops. | Abstract only |
| **Boeing (2017)** | Spatial Tool | OSMnx: Complex street network analysis and manipulation | Street Networks | Network topology, graph centrality | OpenStreetMap global extracts | Tool for network construction; requires routing engine (OSRM) for fast matrix computation. | Full text |
| **Haklay & Weber (2008)**| Spatial Data | OpenStreetMap crowdsourced geographic data quality audit | Geographic POIs | Positional accuracy, completeness | UK Ordnance Survey comparison | Notes spatial coverage in developing nations and tier-2/3 regions is patchy and needs ground census. | Full text |
| **MoP India (2022)** | Policy Norm | Revised consolidated guidelines and standards for EV charging | All EVs | 1 station per 3x3 km (cities); 1 station per 25 km (highways); 1 fast charger per 100 km | National planning standards | Statutory mandate; government maintains no live spatial compliance dataset to evaluate gaps. | Full text |
| **BEE India (2024)** | Policy Norm | National EV charging infrastructure rollout guidelines | All EVs | Siting guidelines, discom power clearances | Central state data | Does not provide district-level or highway-level spatial gap assessment tools. | Full text |
| **UDHD MP (2025)** | State Policy | Madhya Pradesh Electric Vehicle Policy 2025 targets | E2W, E3W, E4W | 10% new registration share by 2027; 5 Model EV Cities | MP urban demographic data | Sets ambitious penetration goals but provides no public charging infrastructure routing or recommendation platform. | Full text |
| **MHI India (2026)** | Official Data | Rajya Sabha Unstarred Question 3910 (answered 27-Mar-2026) | Public Chargers | Installed (1,417) vs Operational (1,291) stations in MP | Ministry of Heavy Industries official registry | Officially confirms that no central EV-to-charger ratio or tier-2/3 highway coverage dataset is maintained. | Full text |

---

## 2. Research Gap Statement (Draft for Thesis & Phase-I Report)

*Draft prepared by Eshwari for peer review and final report integration:*

> "A critical examination of the international literature reveals that prevailing electric vehicle routing models predominantly focus on luxury passenger cars (E4Ws) operating in high-income Western or East Asian contexts (Franke et al., 2012; Schneider et al., 2014; Lee et al., 2019). These systems optimize navigation purely through Euclidean spatial proximity or basic trip time, completely overlooking the socio-technical realities of India's electric mobility transition.
> 
> In Madhya Pradesh, commercial two-wheelers (E2W) and three-wheelers (E3W) constitute over **97.2% of all registered electric vehicles** (CY2024: E2W 49.6%, E3W 47.6%, E4W 2.4%). Yet, current navigation systems (e.g., Google Maps, Open Charge Map) direct drivers exclusively to the **geometrically nearest** charger. This leads to severe systemic inefficiencies: commercial drivers are routed to expensive private hubs, chargers with plugs incompatible with their vehicles, or high-power fast-chargers whose output exceeds the onboard Battery Management System (BMS) acceptance rate, while incurring unpredicted queue wait times.
> 
> Furthermore, while the Ministry of Power (2022) mandates clear infrastructure benchmarks—namely, one charging station per $3 \times 3\text{ km}$ urban grid and one every $25\text{ km}$ along inter-city highways—official parliamentary records (**Ministry of Heavy Industries, Rajya Sabha Unstarred Question 3910, 27 March 2026**) confirm that although 1,417 public stations are installed across Madhya Pradesh (1,291 operational), **no centralized assessment of EV-to-charger density or corridor spacing gaps is maintained by state or central agencies**.
> 
> CERCOS directly fills this dual research gap by:
> 1. Formulating an anchored, multi-criteria recommendation engine (TOPSIS + Best-Worst Method) customized for 2W/3W operational modes that evaluates charging speed as $\min(\text{station\_kW}, \text{vehicle\_max\_accept\_kW})$ alongside tariffs, queue times, and detour penalties.
> 2. Developing an empirical, spatial corridor gap analysis tool (`corridor_spacing_v0.py`) benchmarked directly against statutory Ministry of Power norms across the Bhopal capital region."
