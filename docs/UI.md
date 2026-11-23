# CERCOS Frontend & UI Documentation

**Owner:** Anshuman  
**Area:** Frontend map application & Field Mode instruments  
**Phase-I Scope:** P4 UI MVP + P3 Field Mode Forms (7% share of 40%)

---

## 1. Overview & Architecture

The CERCOS frontend provides an intuitive, responsive, and mobile-friendly web application for two primary purposes:
1. **Driver EV Recommendation UI:** Allows EV drivers (e-2W, e-3W, e-4W, fleets) to input their trip origin, destination, current battery State of Charge (SoC), vehicle segment, and preferred routing mode, returning the top 3 optimal charging stops recommended by the TOPSIS engine alongside explanations and nearest-charger comparisons.
2. **Field Mode Instruments (PWA):** Offline-first mobile forms for student enumerator pairs in the Bhopal region to conduct charging station censuses, anonymous driver preference surveys (Best-Worst Method), and charging station queue counts.

```
frontend/
├── index.html                   # HTML entry with responsive viewport (supports >=360px)
├── src/
│   ├── main.tsx                 # Application mount & MSW service worker lifecycle
│   ├── App.tsx                  # Root layout containing header, Mock banner, and map viewport
│   ├── App.css / index.css      # Responsive styles & viewport resets
│   ├── components/
│   │   ├── MapView.tsx          # Leaflet map centred on Bhopal (23.26° N, 77.41° E, Zoom 11)
│   │   └── MockBanner.tsx       # Visible badge indicating synthetic/mock mode
│   ├── api/
│   │   ├── types.ts             # Auto-generated TypeScript interfaces from contracts/openapi.draft.yaml
│   │   └── client.ts            # Strongly-typed fetch client for /v1/* endpoints
│   ├── mocks/
│   │   ├── handlers.ts          # MSW handlers adhering to contracts/engine_interface.md
│   │   └── browser.ts           # Browser-based service worker worker setup
│   └── test/
│       ├── setup.ts             # Vitest DOM matchers setup
│       └── App.test.tsx         # Automated smoke tests for map container and layout
```

---

## 2. Bhopal Base Map Configuration

- **Coordinates:** Centred at Latitude `23.2599` N, Longitude `77.4126` E (Bhopal City Centre).
- **Default Zoom:** Level `11` (covering the central city and immediate approach corridors).
- **Tiles:** OpenStreetMap Standard tile layer (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`).
- **Attribution:** Fully visible attribution to `© OpenStreetMap contributors`.
- **Responsive Layout:** Responsive layout spanning 100% viewport height (`100dvh`), tested down to $360\text{ px}$ width for mobile devices.

---

## 3. Mock Strategy & Engine Contract

To ensure frontend development is decoupled from backend deployment, CERCOS utilizes Mock Service Worker (MSW):
- When `VITE_USE_MOCKS=true` (or unset), MSW intercepts network requests in the browser.
- Returned recommendation results strictly match `contracts/engine_interface.md`:
  - `top3` stations with multi-criteria scores, rank, detour km, cost, estimated wait, and arrival SoC.
  - Transparent `explain` arrays breaking down criterion weights and contributions.
  - Required data provenance tags (`source: "synthetic"`, `confidence: 0.95`).
- A visible **"Mock data"** banner is rendered in the UI whenever synthetic mocks are active.

---

## 4. Developer Commands

From `cercos/CERCOS-team-pack/CERCOS/frontend`:

```bash
# Install dependencies
npm ci

# Start local development server (with Leaflet map and Mock banner)
npm run dev

# Run TypeScript compilation and production build
npm run build

# Run code style and ESLint rules
npm run lint

# Run automated Vitest test suite
npm test
```
