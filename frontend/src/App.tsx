import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { MapView } from './components/MapView'
import { MockBanner } from './components/MockBanner'
import {
  cercosApi,
  type LatLon,
  type RecommendResult,
  type StationFeature,
  type SystemStatusResponse,
  type VehicleProfile,
} from './api/client'
import './App.css'

interface CorridorPreset {
  id: string
  label: string
  origin: LatLon
  destination: LatLon
  routeKm: number
}

const CORRIDOR_PRESETS: CorridorPreset[] = [
  {
    id: 'bhopal-ashta',
    label: 'Bhopal → Ashta (NH-46 · ~85 km)',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 23.0195, lon: 76.7222 },
    routeKm: 85.0,
  },
  {
    id: 'bhopal-indore',
    label: 'Bhopal → Indore Full Corridor (~195 km)',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 22.7196, lon: 75.8577 },
    routeKm: 195.0,
  },
  {
    id: 'bhopal-sehore',
    label: 'Bhopal → Sehore / VIT Bhopal (~45 km)',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 23.074, lon: 76.8298 },
    routeKm: 45.0,
  },
  {
    id: 'bhopal-vidisha',
    label: 'Bhopal → Vidisha Regional Route (~58 km)',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 23.5226, lon: 77.8148 },
    routeKm: 58.0,
  },
  {
    id: 'bhopal-urban',
    label: 'Bhopal Urban Loop (~22 km · E2W/E3W friendly)',
    origin: { lat: 23.2338, lon: 77.4319 },
    destination: { lat: 23.2712, lon: 77.3385 },
    routeKm: 22.0,
  },
]

const ALL_MP_BBOX = '75.0,22.0,79.0,24.5'

type AppTab = 'map' | 'field' | 'audit'

export const App: React.FC = () => {
  const useMocks = import.meta.env.VITE_USE_MOCKS !== 'false'

  const [activeTab, setActiveTab] = useState<AppTab>('map')
  const [stations, setStations] = useState<StationFeature[]>([])
  const [vehicles, setVehicles] = useState<VehicleProfile[]>([])
  const [modes, setModes] = useState<string[]>([
    'Balanced',
    'Cheapest',
    'Fastest',
    'Shortest',
    'HighestRated',
    'BatterySafe',
  ])
  const [statusInfo, setStatusInfo] = useState<SystemStatusResponse | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)

  // Optimizer form state
  const [selectedPresetId, setSelectedPresetId] = useState<string>('bhopal-ashta')
  const [selectedVehicleIdx, setSelectedVehicleIdx] = useState<number>(4) // Tata Nexon EV 45
  const [socPct, setSocPct] = useState<number>(35)
  const [selectedMode, setSelectedMode] = useState<string>('Balanced')
  const [loadingRec, setLoadingRec] = useState<boolean>(false)
  const [recommendation, setRecommendation] = useState<RecommendResult | null>(null)
  const [selectedStation, setSelectedStation] = useState<StationFeature | null>(null)

  // Field form states
  const [censusName, setCensusName] = useState('')
  const [censusCpo, setCensusCpo] = useState('Tata Power')
  const [censusLat, setCensusLat] = useState('23.2326')
  const [censusLon, setCensusLon] = useState('77.4299')
  const [censusKw, setCensusKw] = useState('60')
  const [censusTariff, setCensusTariff] = useState('18.5')
  const [fieldMsg, setFieldMsg] = useState<string | null>(null)

  const [surveyConsent, setSurveyConsent] = useState(false)
  const [surveySegment, setSurveySegment] = useState<'E2W' | 'E3W' | 'E4W' | 'ELCV'>('E3W')
  const [surveyBest, setSurveyBest] = useState('cost')
  const [surveyWorst, setSurveyWorst] = useState('rating')

  const activePreset = useMemo(
    () => CORRIDOR_PRESETS.find((p) => p.id === selectedPresetId) || CORRIDOR_PRESETS[0],
    [selectedPresetId],
  )

  const activeVehicle = useMemo(
    () => vehicles[selectedVehicleIdx] || vehicles[0] || null,
    [vehicles, selectedVehicleIdx],
  )

  const stationNameById = useMemo(() => {
    const map = new Map<number, string>()
    stations.forEach((st) => {
      map.set(st.properties.station_id, st.properties.name || st.properties.station_name || `Station #${st.properties.station_id}`)
    })
    return map
  }, [stations])

  const rejectedSummary = useMemo(() => {
    const list = recommendation?.rejected ?? []
    let mismatch = 0
    let unreachable = 0
    let offline = 0
    for (const item of list) {
      const lower = item.reason.toLowerCase()
      if (lower.includes('connector mismatch')) mismatch += 1
      else if (lower.includes('unreachable') || lower.includes('reserve')) unreachable += 1
      else offline += 1
    }
    const parts: string[] = []
    if (mismatch > 0) parts.push(`${mismatch} connector mismatch`)
    if (unreachable > 0) parts.push(`${unreachable} below 8% safety reserve`)
    if (offline > 0) parts.push(`${offline} out of service`)
    return {
      total: list.length,
      breakdown: parts.join(', '),
    }
  }, [recommendation])

  // Load initial stations, vehicles, modes, and system status from live backend
  const loadInitialData = useCallback(async () => {
    try {
      setApiError(null)
      const [stationFC, vehList, modesResp, sysStatus] = await Promise.all([
        cercosApi.getStations(ALL_MP_BBOX),
        cercosApi.getVehicles(),
        cercosApi.getModes(),
        cercosApi.getStatus().catch(() => null),
      ])

      setStations(stationFC.features)
      setVehicles(vehList)
      if (modesResp.modes) {
        setModes(Array.isArray(modesResp.modes) ? modesResp.modes : Object.keys(modesResp.modes))
      }
      if (sysStatus) setStatusInfo(sysStatus)

      // Pick Tata Nexon EV (E4W) as initial selection if present
      const e4wIdx = vehList.findIndex((v) => v.segment === 'E4W')
      if (e4wIdx >= 0) setSelectedVehicleIdx(e4wIdx)
    } catch (err) {
      setApiError(err instanceof Error ? err.message : 'Unable to reach CERCOS backend API')
    }
  }, [])

  useEffect(() => {
    loadInitialData()
  }, [loadInitialData])

  const runOptimize = useCallback(async () => {
    setLoadingRec(true)
    setApiError(null)
    try {
      const veh = vehicles[selectedVehicleIdx] || vehicles[0]
      const res = await cercosApi.recommend({
        origin: activePreset.origin,
        destination: activePreset.destination,
        soc_pct: socPct,
        mode: selectedMode as 'Balanced',
        segment: (veh?.segment || 'E4W') as 'E4W',
        vehicle_id: veh?.vehicle_id ?? null,
        route_km: activePreset.routeKm,
      })
      setRecommendation(res)
      if (res.top3.length > 0) {
        const match = stations.find((s) => s.properties.station_id === res.top3[0].station_id)
        if (match) setSelectedStation(match)
      }
    } catch (err) {
      setApiError(err instanceof Error ? err.message : 'Recommendation engine failed')
    } finally {
      setLoadingRec(false)
    }
  }, [vehicles, selectedVehicleIdx, activePreset, socPct, selectedMode, stations])

  // Auto-run first optimization once vehicles & stations finish loading
  useEffect(() => {
    if (stations.length > 0 && vehicles.length > 0 && !recommendation && !useMocks) {
      runOptimize()
    }
  }, [stations.length, vehicles.length, recommendation, useMocks, runOptimize])

  const handleCensusSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFieldMsg(null)
    try {
      const res = await cercosApi.submitCensus({
        station_name: censusName || 'Field Audit EV Hub',
        cpo_name: censusCpo,
        latitude: Number(censusLat),
        longitude: Number(censusLon),
        max_power_kw: Number(censusKw),
        tariff_inr_kwh: Number(censusTariff),
        open_24x7: true,
        is_operational: true,
        connectors: [{ connector_type: 'CCS2', output_power_kw: Number(censusKw), status: 'AVAILABLE' }],
        enumerator: 'Field Team',
      })
      setFieldMsg(`Saved Census Record #${res.id} persistently to database!`)
      setCensusName('')
    } catch (err) {
      setFieldMsg(err instanceof Error ? err.message : 'Census submission failed')
    }
  }

  const handleSurveySubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFieldMsg(null)
    try {
      const res = await cercosApi.submitSurvey({
        consent: surveyConsent,
        segment: surveySegment,
        home_charging: false,
        range_anxiety: 4,
        best_criterion: surveyBest,
        worst_criterion: surveyWorst,
        best_to_others: { [surveyBest]: 1, cost: 2, wait: 3, [surveyWorst]: 7 },
        others_to_worst: { [surveyBest]: 7, cost: 5, wait: 4, [surveyWorst]: 1 },
        wtp_zero_wait_inr: 3.0,
      })
      setFieldMsg(`Saved Anonymized Survey #${res.id} (Consent verified, 0 PII stored).`)
    } catch (err) {
      setFieldMsg(err instanceof Error ? err.message : 'Survey submission blocked')
    }
  }

  const reachableEstimateKm = useMemo(() => {
    if (!activeVehicle) return 0
    const usable = Math.max(0, socPct - 8)
    return Math.round(((usable / 100) * activeVehicle.battery_kwh * 1000) / activeVehicle.wh_per_km)
  }, [activeVehicle, socPct])

  return (
    <div className="cercos-app">
      <MockBanner visible={useMocks} />

      <header className="cercos-header">
        <div className="cercos-brand">
          <h1 className="cercos-title">CERCOS</h1>
          <span className="cercos-subtitle">Cognitive EV Route & Charging Optimization</span>
        </div>

        <nav className="cercos-nav">
          <button
            type="button"
            className={`nav-btn ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
          >
            Corridor Map & Optimizer
          </button>
          <button
            type="button"
            className={`nav-btn ${activeTab === 'field' ? 'active' : ''}`}
            onClick={() => setActiveTab('field')}
          >
            Field Mode & Surveys
          </button>
          <button
            type="button"
            className={`nav-btn ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            Real Data & System Audit
          </button>
        </nav>

        <div className="cercos-header-meta">
          <span className={`cercos-badge ${statusInfo?.database.connected ? 'badge-live' : ''}`}>
            {statusInfo?.database.connected
              ? `Live (${statusInfo.database.backend}) · ${stations.length} Stations`
              : `${stations.length} Stations Loaded`}
          </span>
        </div>
      </header>

      {apiError && (
        <div className="cercos-error-bar">
          <strong>Backend Notice:</strong> {apiError} — ensure FastAPI is running on{' '}
          <code>http://localhost:8000</code>.
        </div>
      )}

      {activeTab === 'map' && (
        <main className="cercos-workspace">
          <aside className="cercos-sidebar">
            <section className="panel-section">
              <h3>1. Route & Corridor</h3>
              <label className="field-label">
                Corridor Route
                <select
                  value={selectedPresetId}
                  onChange={(e) => setSelectedPresetId(e.target.value)}
                >
                  {CORRIDOR_PRESETS.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field-label">
                Vehicle Profile ({vehicles.length} OEM specs)
                <select
                  value={selectedVehicleIdx}
                  onChange={(e) => setSelectedVehicleIdx(Number(e.target.value))}
                >
                  {vehicles.map((v, idx) => (
                    <option key={v.vehicle_id ?? idx} value={idx}>
                      [{v.segment}] {v.model_name} ({v.max_dc_kw ? `${v.max_dc_kw}kW DC` : `${v.max_ac_kw}kW AC`})
                    </option>
                  ))}
                </select>
              </label>

              <label className="field-label">
                Initial Battery SoC: <strong>{socPct}%</strong> · Safe Reach (8% reserve):{' '}
                <strong>{recommendation?.reachable_km ?? reachableEstimateKm} km</strong>
                <input
                  type="range"
                  min={10}
                  max={95}
                  value={socPct}
                  onChange={(e) => setSocPct(Number(e.target.value))}
                />
              </label>

              <div className="mode-grid">
                {modes.map((m) => (
                  <button
                    key={m}
                    type="button"
                    className={`mode-btn ${selectedMode === m ? 'active' : ''}`}
                    onClick={() => setSelectedMode(m)}
                  >
                    {m}
                  </button>
                ))}
              </div>

              <button
                type="button"
                className="primary-cta"
                onClick={runOptimize}
                disabled={loadingRec}
              >
                {loadingRec ? 'Computing Anchored TOPSIS + M/G/c...' : 'Optimize Charging Stop'}
              </button>
            </section>

            {/* Nearest vs CERCOS Comparison Panel (P4 Deliverable) */}
            {recommendation?.nearest_baseline && recommendation.top3.length > 0 && (
              <section className="panel-section comparison-card">
                <h4>Nearest Charger vs CERCOS #1</h4>
                <div className="compare-grid">
                  <div className="compare-col baseline">
                    <span className="col-tag">Naïve Nearest</span>
                    <strong>{recommendation.nearest_baseline.name}</strong>
                    <span>
                      Tariff: ₹{recommendation.nearest_baseline.tariff_inr_kwh}/kWh ·{' '}
                      {recommendation.nearest_baseline.is_compatible ? 'Plug OK' : '⚠ Plug Mismatch!'}
                    </span>
                    <span>
                      Raw {recommendation.nearest_baseline.raw_power_kw}kW → Eff{' '}
                      <strong>{recommendation.nearest_baseline.effective_kw} kW</strong> · Wait{' '}
                      {recommendation.nearest_baseline.wait_min}m
                    </span>
                  </div>
                  <div className="compare-col cercos">
                    <span className="col-tag win">★ CERCOS #1</span>
                    <strong>{recommendation.top3[0].name}</strong>
                    <span>
                      Tariff: ₹{recommendation.top3[0].criteria.cost_inr_kwh}/kWh (
                      {recommendation.nearest_baseline.cost_diff_vs_cercos_inr_kwh >= 0
                        ? `Saves ₹${recommendation.nearest_baseline.cost_diff_vs_cercos_inr_kwh}/kWh`
                        : `+₹${Math.abs(recommendation.nearest_baseline.cost_diff_vs_cercos_inr_kwh)}/kWh`}
                      )
                    </span>
                    <span>
                      Eff <strong>{recommendation.top3[0].criteria.effective_kw} kW</strong> · Wait{' '}
                      {recommendation.top3[0].criteria.wait_min}m · Score{' '}
                      {recommendation.top3[0].score.toFixed(3)}
                    </span>
                  </div>
                </div>
              </section>
            )}

            {/* Top 3 Ranked Results */}
            {recommendation && (
              <section className="panel-section">
                <div className="results-header">
                  <h4>Top Recommended Stops ({recommendation.top3.length})</h4>
                  <span className="engine-ver">{recommendation.engine_version}</span>
                </div>

                {recommendation.top3.length === 0 ? (
                  <div className="empty-warn">
                    No compatible stations reachable with {socPct}% SoC. Increase initial SoC or check rejected reasons.
                  </div>
                ) : (
                  <div className="cards-list">
                    {recommendation.top3.map((st) => (
                      <div
                        key={st.station_id}
                        className={`result-card ${selectedStation?.properties.station_id === st.station_id ? 'selected' : ''}`}
                        onClick={() => {
                          const match = stations.find((f) => f.properties.station_id === st.station_id)
                          if (match) setSelectedStation(match)
                        }}
                      >
                        <div className="card-top">
                          <span className="rank-pill">#{st.rank}</span>
                          <strong>{st.name}</strong>
                          <span className="score-pill">{(st.score * 100).toFixed(1)}%</span>
                        </div>
                        <div className="card-metrics">
                          <span>Eff: {st.criteria.effective_kw} kW</span>
                          <span>Tariff: ₹{st.criteria.cost_inr_kwh}</span>
                          <span>Wait: {st.criteria.wait_min}m</span>
                          <span>Arr SoC: {st.arrival_soc_pct}%</span>
                        </div>
                        <div className="card-metrics">
                          <span>Detour: +{st.criteria.detour_km} km</span>
                          <span>Est Cost: ₹{st.est_cost_inr}</span>
                          <span>Charge: {st.est_charge_min}m</span>
                          <span className="prov-badge">{st.source.toUpperCase()} ({Math.round(st.confidence * 100)}%)</span>
                        </div>
                        <div className="explain-list">
                          {st.explain.slice(0, 3).map((ex, idx) => (
                            <div key={idx} className="explain-item">
                              • {ex.note}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {recommendation.rejected.length > 0 && (
                  <details className="rejected-details">
                    <summary>
                      {rejectedSummary.total} stations filtered out
                      {rejectedSummary.breakdown ? ` (${rejectedSummary.breakdown})` : ' (Hard Constraints)'}
                    </summary>
                    <ul>
                      {recommendation.rejected.slice(0, 25).map((r) => {
                        const stName = stationNameById.get(r.station_id)
                        return (
                          <li key={r.station_id}>
                            <strong>{stName ? `${stName} (#${r.station_id})` : `Station #${r.station_id}`}:</strong>{' '}
                            {r.reason}
                          </li>
                        )
                      })}
                      {recommendation.rejected.length > 25 && (
                        <li>
                          <em>+ {recommendation.rejected.length - 25} additional stations filtered by hard constraints.</em>
                        </li>
                      )}
                    </ul>
                  </details>
                )}
              </section>
            )}
          </aside>

          <div className="cercos-map-pane">
            <MapView
              stations={stations}
              recommendation={recommendation}
              origin={activePreset.origin}
              destination={activePreset.destination}
              selectedStationId={selectedStation?.properties.station_id ?? null}
              onSelectStation={(st) => setSelectedStation(st)}
            />

            {/* Station Detail Drawer */}
            {selectedStation && (
              <div className="cercos-detail-drawer">
                <button
                  type="button"
                  className="drawer-close"
                  onClick={() => setSelectedStation(null)}
                >
                  ✕
                </button>
                <div className="drawer-badges">
                  <span className="prov-badge">{selectedStation.properties.source.toUpperCase()}</span>
                  <span className="conf-badge">
                    Confidence {Math.round((selectedStation.properties.confidence ?? 0.9) * 100)}%
                  </span>
                </div>
                <h4>{selectedStation.properties.name || selectedStation.properties.station_name}</h4>
                <p className="drawer-addr">{selectedStation.properties.address}</p>
                <div className="drawer-specs">
                  <div>
                    <strong>Operator:</strong> {selectedStation.properties.cpo_name || 'Public / Unlisted'}
                  </div>
                  <div>
                    <strong>Max Power:</strong> {selectedStation.properties.max_power_kw ?? 'N/A'} kW
                  </div>
                  <div>
                    <strong>Retail Tariff:</strong>{' '}
                    {selectedStation.properties.tariff_inr_kwh == null
                      ? 'Unlisted (est. ₹18/kWh)'
                      : selectedStation.properties.tariff_inr_kwh === 0
                        ? 'Free (₹0/kWh)'
                        : `₹${selectedStation.properties.tariff_inr_kwh}/kWh`}
                  </div>
                  <div>
                    <strong>Hours:</strong> {selectedStation.properties.hours_text || '24/7'}
                  </div>
                  <div>
                    <strong>OSM / Census Ref:</strong>{' '}
                    <code>{selectedStation.properties.source_ref || 'verified'}</code>
                  </div>
                </div>
                <div className="drawer-connectors">
                  {(selectedStation.properties.connectors || []).map((c, idx) => (
                    <span key={idx} className="conn-tag">
                      {c.connector_type} · {c.output_power_kw}kW
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>
      )}

      {activeTab === 'field' && (
        <main className="cercos-page-grid">
          <div className="page-card">
            <h3>Station Hardware Census (Instrument 1)</h3>
            <p className="muted">
              Persisted directly to CERCOS database via <code>POST /v1/field/census</code>.
            </p>
            <form onSubmit={handleCensusSubmit} className="cercos-form">
              <label className="field-label">
                Station Name
                <input
                  value={censusName}
                  onChange={(e) => setCensusName(e.target.value)}
                  placeholder="e.g. Tatya Tope Nagar EV Point"
                  required
                />
              </label>
              <label className="field-label">
                Operator (CPO)
                <input value={censusCpo} onChange={(e) => setCensusCpo(e.target.value)} />
              </label>
              <div className="form-row">
                <label className="field-label">
                  Latitude
                  <input value={censusLat} onChange={(e) => setCensusLat(e.target.value)} />
                </label>
                <label className="field-label">
                  Longitude
                  <input value={censusLon} onChange={(e) => setCensusLon(e.target.value)} />
                </label>
              </div>
              <div className="form-row">
                <label className="field-label">
                  Max Power (kW)
                  <input value={censusKw} onChange={(e) => setCensusKw(e.target.value)} />
                </label>
                <label className="field-label">
                  Tariff (INR/kWh)
                  <input value={censusTariff} onChange={(e) => setCensusTariff(e.target.value)} />
                </label>
              </div>
              <button type="submit" className="primary-cta">
                Submit Hardware Audit
              </button>
            </form>
          </div>

          <div className="page-card">
            <h3>Anonymous Driver BWM Survey (Instrument 2)</h3>
            <p className="muted">
              Consent required (<code>consent=True</code>). Zero names or phone numbers stored.
            </p>
            <form onSubmit={handleSurveySubmit} className="cercos-form">
              <label className="consent-box">
                <input
                  type="checkbox"
                  checked={surveyConsent}
                  onChange={(e) => setSurveyConsent(e.target.checked)}
                />
                <span>
                  I confirm the participant gave informed verbal consent (mandatory before saving).
                </span>
              </label>
              <label className="field-label">
                Vehicle Segment
                <select
                  value={surveySegment}
                  onChange={(e) =>
                    setSurveySegment(e.target.value as 'E2W' | 'E3W' | 'E4W' | 'ELCV')
                  }
                >
                  <option value="E2W">Electric Two-Wheeler (E2W)</option>
                  <option value="E3W">Electric Three-Wheeler / E-Rickshaw (E3W)</option>
                  <option value="E4W">Electric Four-Wheeler Car (E4W)</option>
                  <option value="ELCV">Electric Light Commercial Vehicle (ELCV)</option>
                </select>
              </label>
              <div className="form-row">
                <label className="field-label">
                  Most Important (Best)
                  <select value={surveyBest} onChange={(e) => setSurveyBest(e.target.value)}>
                    <option value="cost">Charging Cost (INR/kWh)</option>
                    <option value="wait">Queue Wait Time</option>
                    <option value="detour">Detour Distance</option>
                    <option value="speed">Charging Speed</option>
                    <option value="soc">Arrival Battery Safety</option>
                  </select>
                </label>
                <label className="field-label">
                  Least Important (Worst)
                  <select value={surveyWorst} onChange={(e) => setSurveyWorst(e.target.value)}>
                    <option value="rating">Amenities / Rating</option>
                    <option value="detour">Detour Distance</option>
                    <option value="speed">Fast Charger Speed</option>
                  </select>
                </label>
              </div>
              <button type="submit" className="primary-cta">
                Submit Consented Survey
              </button>
            </form>

            {fieldMsg && <div className="field-toast">{fieldMsg}</div>}

            <div className="export-row">
              <strong>Live CSV Data Exports:</strong>
              <div className="export-links">
                <a href={cercosApi.getExportUrl('census')} target="_blank" rel="noreferrer">
                  Census CSV
                </a>
                <a href={cercosApi.getExportUrl('survey')} target="_blank" rel="noreferrer">
                  Survey CSV
                </a>
                <a href={cercosApi.getExportUrl('queue')} target="_blank" rel="noreferrer">
                  Queue CSV
                </a>
              </div>
            </div>
          </div>
        </main>
      )}

      {activeTab === 'audit' && (
        <main className="cercos-page-grid single">
          <div className="page-card">
            <h3>Real Data Provenance & System Verification</h3>
            {statusInfo && (
              <div className="audit-stats">
                <div className="stat-box">
                  <span className="stat-lbl">Database Engine</span>
                  <strong>{statusInfo.database.backend}</strong>
                </div>
                <div className="stat-box">
                  <span className="stat-lbl">Active Corridor Stations</span>
                  <strong>{statusInfo.stations_total}</strong>
                </div>
                <div className="stat-box">
                  <span className="stat-lbl">MHI Official MP Stations</span>
                  <strong>
                    {statusInfo.policy_benchmarks?.mhi_rajya_sabha_q3910_2026_03_27?.omc_stations_operational ?? 1291}{' '}
                    / 1,417
                  </strong>
                </div>
                <div className="stat-box">
                  <span className="stat-lbl">MoP Statutory Highway Spacing</span>
                  <strong>25 km Max</strong>
                </div>
              </div>
            )}

            <table className="audit-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Station Name</th>
                  <th>Operator</th>
                  <th>Coordinates</th>
                  <th>Max kW</th>
                  <th>Tariff</th>
                  <th>Source Reference</th>
                </tr>
              </thead>
              <tbody>
                {stations.map((s) => (
                  <tr
                    key={s.properties.station_id}
                    onClick={() => {
                      setSelectedStation(s)
                      setActiveTab('map')
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>{s.properties.station_id}</td>
                    <td>{s.properties.name || s.properties.station_name}</td>
                    <td>{s.properties.cpo_name}</td>
                    <td>
                      {s.geometry.coordinates[1].toFixed(4)}, {s.geometry.coordinates[0].toFixed(4)}
                    </td>
                    <td>{s.properties.max_power_kw} kW</td>
                    <td>₹{s.properties.tariff_inr_kwh}</td>
                    <td>
                      <code>{s.properties.source_ref || s.properties.source}</code>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      )}
    </div>
  )
}

export default App
