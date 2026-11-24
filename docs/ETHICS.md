# CERCOS Field Research Ethics & Informed Consent Framework

```text
================================================================================
DRAFT — PENDING FORMAL FACULTY ETHICAL CLEARANCE
Approved by Faculty Supervisor: _________________________  Date: ______________
Reviewer 1 Signature:          _________________________  Date: ______________
Reviewer 2 Signature:          _________________________  Date: ______________
================================================================================
```

**Lead:** Kashish (Field Research Lead)  
**Programme:** EPICS (Engineering Project in Community Service), VIT Bhopal University  
**Project:** Cognitive EV Route and Charging Optimization System (CERCOS)  

---

## 1. Ethical Principles & Research Commitments

This field study complies with the research guidelines of VIT Bhopal University and standard ethical conventions for non-invasive academic transportation surveys:

1. **Informed Voluntary Consent:** No driver, fleet operator, or station attendant is surveyed without receiving clear, upfront verbal disclosure of the study's purpose and granting explicit consent.
2. **Right to Withdraw:** Participants may pause, skip specific questions, or withdraw completely at any point during the questionnaire without penalty or explanation.
3. **Strict Anonymity (Zero PII):** We collect zero personally identifiable information (PII). No personal names, telephone numbers, home addresses, license numbers, employer identities, or vehicle registration plate numbers are ever recorded.
4. **Non-Invasive Observation:** Station census and queue observations are purely observational. Team members never obstruct charging bays, never interfere with high-voltage electrical hardware, and never photograph human faces.
5. **No Commercial Exploitation:** All collected data is used exclusively for undergraduate EPICS research and academic open-source publication. Data is never sold, shared with marketing agencies, or monetized.

---

## 2. Verbal Informed Consent Scripts

Field enumerators must read the following script aloud to every prospective respondent prior to recording any data:

### English Script
> *"Hello! We are undergraduate engineering students from VIT Bhopal University working on an academic research project called CERCOS. We are studying electric vehicle charging experiences and infrastructure needs across Madhya Pradesh.*  
>  
> *May we ask you a few brief questions about your daily travel, vehicle charging preferences, and what matters most to you when choosing a charging station? It will take about 4 to 5 minutes.*  
>  
> *This survey is completely voluntary and 100% anonymous. We do not ask for your name, phone number, or vehicle number plate. Your answers will only be used for our university research report.*  
>  
> *Do you agree to participate?"*

### Hindi Script *(Needs native-speaker validation)*
> *"नमस्ते! हम वीआईटी भोपाल यूनिवर्सिटी के इंजीनियरिंग के छात्र हैं। हम मध्य प्रदेश में इलेक्ट्रिक वाहन (EV) चार्जिंग की सुविधाओं और चालकों की प्राथमिकताओं पर एक शैक्षणिक रिसर्च प्रोजेक्ट (CERCOS) कर रहे हैं।*  
>  
> *क्या हम आपसे आपकी गाड़ी की चार्जिंग, यात्रा और प्राथमिकताओं के बारे में कुछ सवाल पूछ सकते हैं? इसमें केवल 4 से 5 मिनट का समय लगेगा।*  
>  
> *यह सर्वे पूरी तरह से स्वैच्छिक और गोपनीय (anonymous) है। हम आपका नाम, फोन नंबर या गाड़ी का नंबर नहीं पूछेंगे। आपके जवाब केवल हमारे कॉलेज के शोध के लिए उपयोग किए जाएंगे।*  
>  
> *क्या आप इस सर्वे में भाग लेने के लिए सहमत हैं?"*

---

## 3. Data Classification: What We Collect vs. What We Do NOT Collect

| Category | Explicitly Collected | Strictly PROHIBITED (Never Collected) |
|---|---|---|
| **Identity** | None. Anonymous surrogate ID (`response_id`) only. | Driver Name, Nickname, Signature, Contact Details |
| **Contact** | None. | Mobile Number, Email, WhatsApp, Social Handles |
| **Vehicle** | Vehicle Category (`E2W`, `E3W`, `E4W`), Model Name, Battery kWh (if known) | Vehicle Registration Number Plate (RC), Chassis / VIN Number |
| **Location** | General origin/destination area (e.g., *"Bhopal to Ashta"*), Station GPS | Home Street Address, Exact Residential GPS Coordinates |
| **Imagery** | Equipment nameplate photo, tariff board photo | Human Faces, Drivers, Attendants, Bystanders, License Plates |
| **Finances** | Stated tariff (INR/kWh), Willingness-to-pay (WTP) | Bank Account Numbers, UPI IDs, Transaction Receipts |

---

## 4. Data Storage, Access Control & Deletion Schedule

1. **Storage Tier 1 (Raw Forms & Media):**
   - Physical paper survey sheets and equipment photographs are stored in a password-protected, university-managed Google Drive folder.
   - Access is restricted exclusively to the six student investigators (Ansh, Atharva, Yash, Anshuman, Kashish, Eshwari) and the faculty supervisor.
2. **Storage Tier 2 (Public Repository):**
   - Only sanitized, fully anonymized CSV files containing no free-text personal notes are placed in `data/field/processed/` within the GitHub repository.
3. **Data Retention & Disposal:**
   - Raw paper sheets and unredacted media will be permanently destroyed upon completion and official grading of the EPICS curriculum:
   - **Target Data Deletion Date:** `30 June 2027`
