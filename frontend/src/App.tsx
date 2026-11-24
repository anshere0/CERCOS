import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { LandingOverlay } from './components/LandingOverlay'
import { MapView } from './components/MapView'
import { MockBanner } from './components/MockBanner'
import {
  cercosApi,
  formatTariff,
  type LatLon,
  type RecommendResult,
  type RouteResponse,
  type RouteStep,
  type StationFeature,
  type SystemStatusResponse,
  type VehicleProfile,
} from './api/client'
import './App.css'

interface CorridorPreset {
  id: string
  label: string
  originLabel: string
  destLabel: string
  origin: LatLon
  destination: LatLon
  routeKm: number
}

const CORRIDOR_PRESETS: CorridorPreset[] = [
  {
    id: 'bhopal-ashta',
    label: 'Bhopal → Ashta (NH-46 · ~85 km)',
    originLabel: 'Bhopal (Arera Hills)',
    destLabel: 'Ashta Highway Interchange',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 23.0195, lon: 76.7222 },
    routeKm: 85.0,
  },
  {
    id: 'bhopal-indore',
    label: 'Bhopal → Indore Full Corridor (~195 km)',
    originLabel: 'Bhopal Central',
    destLabel: 'Indore (Rajwada / AB Rd)',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 22.7196, lon: 75.8577 },
    routeKm: 195.0,
  },
  {
    id: 'bhopal-sehore',
    label: 'Bhopal → Sehore / VIT Bhopal (~45 km)',
    originLabel: 'Bhopal City',
    destLabel: 'VIT Bhopal (Kothri Kalan)',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 23.074, lon: 76.8298 },
    routeKm: 45.0,
  },
  {
    id: 'bhopal-vidisha',
    label: 'Bhopal → Vidisha Regional Route (~58 km)',
    originLabel: 'Bhopal Junction',
    destLabel: 'Vidisha Town',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 23.5226, lon: 77.8148 },
    routeKm: 58.0,
  },
  {
    id: 'bhopal-urban',
    label: 'Bhopal Urban Loop (~22 km · E2W/E3W friendly)',
    originLabel: 'MP Nagar Zone 1',
    destLabel: 'Bairagarh / Bhojtal West',
    origin: { lat: 23.2338, lon: 77.4319 },
    destination: { lat: 23.2712, lon: 77.3385 },
    routeKm: 22.0,
  },
]

const ALL_MP_BBOX = '75.0,22.0,79.0,24.5'

type AppTab = 'map' | 'field' | 'audit'
type DrawerTab = 'setup' | 'directions'
type SheetMode = 'peek' | 'half' | 'full'

function maneuverArrow(type: string, modifier?: string | null): string {
  if (type === 'arrive') return '🏁'
  if (type === 'depart') return '🧭'
  if (type === 'roundabout' || type === 'rotary') return '⟳'
  const mod = (modifier || '').toLowerCase()
  if (mod.includes('left')) return '↰'
  if (mod.includes('right')) return '↱'
  return '↑'
}

export const App: React.FC = () => {
  const useMocks = import.meta.env.VITE_USE_MOCKS !== 'false'

  const [activeTab, setActiveTab] = useState<AppTab>('map')
  const [showLanding, setShowLanding] = useState<boolean>(true)
  const [panelCollapsed, setPanelCollapsed] = useState<boolean>(false)
  const [drawerTab, setDrawerTab] = useState<DrawerTab>('setup')
  const [mobileSheet, setMobileSheet] = useState<SheetMode>('peek')

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

  const [selectedPresetId, setSelectedPresetId] = useState<string>('bhopal-ashta')
  const [selectedVehicleIdx, setSelectedVehicleIdx] = useState<number>(4)
  const [socPct, setSocPct] = useState<number>(35)
  const [selectedMode, setSelectedMode] = useState<string>('Balanced')

  const [recommendation, setRecommendation] = useState<RecommendResult | null>(null)
  const [routeData, setRouteData] = useState<RouteResponse | null>(null)
  const [loadingRec, setLoadingRec] = useState<boolean>(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [selectedStation, setSelectedStation] = useState<StationFeature | null>(null)
  const [focusedStepLoc, setFocusedStepLoc] = useState<[number, number] | null>(null)

  // Live Google Maps Route Preview Simulator state
  const [simActive, setSimActive] = useState<boolean>(false)
  const [simIdx, setSimIdx] = useState<number>(0)

  // Field Mode states
  const [censusName, setCensusName] = useState('')
  const [censusCpo, setCensusCpo] = useState('Tata Power EZ Charge')
  const [censusLat, setCensusLat] = useState('23.2512')
  const [censusLon, setCensusLon] = useState('77.4198')
  const [censusKw, setCensusKw] = useState('60')
  const [censusTariff, setCensusTariff] = useState('19')
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
      map.set(
        st.properties.station_id,
        st.properties.name || st.properties.station_name || `Station #${st.properties.station_id}`,
      )
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
    setSimActive(false)
    setSimIdx(0)
    try {
      const veh = vehicles[selectedVehicleIdx]
      const res = await cercosApi.recommend({
        origin: activePreset.origin,
        destination: activePreset.destination,
        soc_pct: socPct,
        mode: selectedMode as
          | 'Balanced'
          | 'Cheapest'
          | 'Fastest'
          | 'Shortest'
          | 'HighestRated'
          | 'BatterySafe',
        segment: veh?.segment || 'E4W',
        vehicle_model: veh?.model_name,
        route_km: activePreset.routeKm,
      })
      setRecommendation(res)

      const top1 = res.top3[0]
      if (top1) {
        const match = stations.find((s) => s.properties.station_id === top1.station_id)
        if (match) setSelectedStation(match)
      }

      const routeRes = await cercosApi
        .getRoute({
          origin: activePreset.origin,
          destination: activePreset.destination,
          waypoint:
            top1?.lat != null && top1?.lon != null ? { lat: top1.lat, lon: top1.lon } : null,
          waypoint_name: top1?.name ?? null,
        })
        .catch(() => null)
      if (routeRes) setRouteData(routeRes)
    } catch (err) {
      setApiError(err instanceof Error ? err.message : 'Recommendation engine failed')
    } finally {
      setLoadingRec(false)
    }
  }, [vehicles, selectedVehicleIdx, activePreset, socPct, selectedMode, stations])

  useEffect(() => {
    if (stations.length > 0 && vehicles.length > 0 && !recommendation && !useMocks) {
      runOptimize()
    }
  }, [stations.length, vehicles.length, recommendation, useMocks, runOptimize])

  // Flatten detailed street route vertices & steps for live Drive Preview animation
  const simPathCoords = useMemo<[number, number][]>(() => {
    if (!routeData) return []
    const pts: [number, number][] = []
    routeData.legs.forEach((leg) => {
      leg.coordinates.forEach((c) => pts.push(c))
    })
    return pts
  }, [routeData])

  const simSteps = useMemo<RouteStep[]>(() => {
    if (!routeData) return []
    return routeData.legs.flatMap((l) => l.steps)
  }, [routeData])

  useEffect(() => {
    if (!simActive || simPathCoords.length === 0) return
    const timer = window.setInterval(() => {
      setSimIdx((prev) => {
        const next = prev + Math.max(1, Math.floor(simPathCoords.length / 80))
        if (next >= simPathCoords.length) {
          setSimActive(false)
          return 0
        }
        return next
      })
    }, 180)
    return () => window.clearInterval(timer)
  }, [simActive, simPathCoords.length])

  const simPosition = simActive && simPathCoords.length > 0 ? simPathCoords[simIdx] ?? null : null
  const simStep = useMemo(() => {
    if (!simActive || simSteps.length === 0 || simPathCoords.length === 0) return null
    const ratio = simIdx / Math.max(1, simPathCoords.length - 1)
    const idx = Math.min(simSteps.length - 1, Math.floor(ratio * simSteps.length))
    return simSteps[idx] ?? null
  }, [simActive, simSteps, simIdx, simPathCoords.length])

  const handleToggleSim = () => {
    if (simPathCoords.length === 0) return
    setSimIdx(0)
    setSimActive((prev) => !prev)
  }

  const handleSelectCorridorFromLanding = (presetId: string) => {
    setSelectedPresetId(presetId)
    setRecommendation(null)
    setShowLanding(false)
    setActiveTab('map')
    setPanelCollapsed(false)
    setDrawerTab('directions')
  }

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

  const cycleMobileSheet = () => {
    setMobileSheet((prev) => (prev === 'peek' ? 'half' : prev === 'half' ? 'full' : 'peek'))
  }

  return (
    <div className="cercos-app">
      <MockBanner visible={useMocks} />

      <header className="cercos-header">
        <div className="cercos-brand">
          <div className="brand-mark">⚡</div>
          <h1 className="cercos-title">CERCOS</h1>
          <span className="cercos-subtitle">Cognitive EV Route & Charging Optimization</span>
        </div>

        <nav className="cercos-nav">
          <button
            type="button"
            className={`nav-btn ${activeTab === 'map' && showLanding ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('map')
              setShowLanding(true)
            }}
          >
            Overview
          </button>
          <button
            type="button"
            className={`nav-btn ${activeTab === 'map' && !showLanding ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('map')
              setShowLanding(false)
            }}
          >
            Navigator Map
          </button>
          <button
            type="button"
            className={`nav-btn ${activeTab === 'field' ? 'active' : ''}`}
            onClick={() => {
              setShowLanding(false)
              setActiveTab('field')
            }}
          >
            Field Mode
          </button>
          <button
            type="button"
            className={`nav-btn ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => {
              setShowLanding(false)
              setActiveTab('audit')
            }}
          >
            System Audit
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
          {/* Full-Bleed Map Container Always Mounted Behind Floating Directions & Landing */}
          <div className="cercos-map-pane">
            <MapView
              stations={stations}
              recommendation={recommendation}
              routeData={routeData}
              origin={activePreset.origin}
              destination={activePreset.destination}
              selectedStationId={selectedStation?.properties.station_id ?? null}
              focusedStepLoc={focusedStepLoc}
              simActive={simActive}
              simPosition={simPosition}
              simStep={simStep}
              onToggleSim={routeData ? handleToggleSim : undefined}
              onSelectStation={(st) => setSelectedStation(st)}
              onOpenLanding={() => setShowLanding(true)}
            />

            {/* Floating Google Maps Directions & Route Drawer (Desktop Floating / Mobile Bottom Sheet) */}
            {!showLanding && (
              <>
                {panelCollapsed ? (
                  <button
                    type="button"
                    className="floating-expand-pill"
                    onClick={() => setPanelCollapsed(false)}
                  >
                    🧭 Directions &amp; EV Stops ({recommendation?.top3.length ?? 0})
                  </button>
                ) : (
                  <aside className={`gmaps-directions-drawer sheet-${mobileSheet}`}>
                    <div
                      className="mobile-sheet-handle-row"
                      onClick={cycleMobileSheet}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') cycleMobileSheet()
                      }}
                    >
                      <span className="sheet-grab-bar" />
                      <div className="sheet-peek-summary">
                        <strong>
                          {recommendation?.top3[0]?.name || activePreset.label}
                        </strong>
                        <span className="mono">
                          {routeData
                            ? `${routeData.total_distance_km} km · ${Math.round(routeData.total_duration_min)}m drive`
                            : `${activePreset.routeKm} km route`}
                          {recommendation?.top3[0]
                            ? ` · ★ #1 ₹${recommendation.top3[0].criteria.cost_inr_kwh}/kWh`
                            : ''}
                        </span>
                      </div>
                      <span className="sheet-toggle-lbl">
                        {mobileSheet === 'full' ? 'Minimize' : 'Expand'}
                      </span>
                    </div>

                    <div className="drawer-top-strip">
                      <div className="drawer-tabs">
                        <button
                          type="button"
                          className={`d-tab ${drawerTab === 'setup' ? 'active' : ''}`}
                          onClick={() => setDrawerTab('setup')}
                        >
                          EV Route &amp; Stops
                        </button>
                        <button
                          type="button"
                          className={`d-tab ${drawerTab === 'directions' ? 'active' : ''}`}
                          onClick={() => setDrawerTab('directions')}
                        >
                          Turn-by-Turn ({simSteps.length})
                        </button>
                      </div>
                      <button
                        type="button"
                        className="collapse-drawer-btn"
                        onClick={() => setPanelCollapsed(true)}
                        title="Hide Panel for Full Map"
                      >
                        ◀
                      </button>
                    </div>

                    <div className="drawer-scroll-body">
                      {/* Visual Google Maps Origin -> EV Stop -> Destination Route Box */}
                      <div className="gmaps-route-box">
                        <div className="route-rail">
                          <span className="rail-dot origin" />
                          <span className="rail-line" />
                          <span className="rail-dot stop">⚡</span>
                          <span className="rail-line" />
                          <span className="rail-dot dest" />
                        </div>
                        <div className="route-fields">
                          <div className="route-row-pill">
                            <small>ORIGIN</small>
                            <strong>{activePreset.originLabel}</strong>
                          </div>
                          <div className="route-row-pill stop-pill">
                            <small>OPTIMAL CHARGE STOP</small>
                            <strong>
                              {recommendation?.top3[0]?.name || 'Computing best stop...'}
                            </strong>
                          </div>
                          <div className="route-row-pill">
                            <small>DESTINATION</small>
                            <strong>{activePreset.destLabel}</strong>
                          </div>
                        </div>
                      </div>

                      {drawerTab === 'setup' && (
                        <>
                          <section className="panel-section">
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
                                    [{v.segment}] {v.model_name} (
                                    {v.max_dc_kw ? `${v.max_dc_kw}kW DC` : `${v.max_ac_kw}kW AC`})
                                  </option>
                                ))}
                              </select>
                            </label>

                            <label className="field-label">
                              Battery SoC: <strong>{socPct}%</strong> · Safe Reach (8% reserve):{' '}
                              <strong className="mono">
                                {recommendation?.reachable_km ?? reachableEstimateKm} km
                              </strong>
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

                            <div className="action-btn-row">
                              <button
                                type="button"
                                className="primary-cta"
                                onClick={runOptimize}
                                disabled={loadingRec}
                              >
                                {loadingRec ? 'Routing...' : 'Optimize Stop'}
                              </button>
                              {routeData && (
                                <button
                                  type="button"
                                  className={`sim-cta ${simActive ? 'active' : ''}`}
                                  onClick={handleToggleSim}
                                >
                                  {simActive ? '⏹ Stop' : '▶ Preview Drive'}
                                </button>
                              )}
                            </div>
                          </section>

                          {recommendation?.nearest_baseline && recommendation.top3.length > 0 && (
                            <section className="panel-section comparison-card">
                              <h4>Nearest Charger vs CERCOS #1</h4>
                              <div className="compare-grid">
                                <div className="compare-col baseline">
                                  <span className="col-tag">Naïve Nearest</span>
                                  <strong>{recommendation.nearest_baseline.name}</strong>
                                  <span>
                                    Tariff: ₹{recommendation.nearest_baseline.tariff_inr_kwh}/kWh ·{' '}
                                    {recommendation.nearest_baseline.is_compatible
                                      ? 'Plug OK'
                                      : '⚠ Plug Mismatch!'}
                                  </span>
                                  <span>
                                    Raw {recommendation.nearest_baseline.raw_power_kw}kW → Eff{' '}
                                    <strong>{recommendation.nearest_baseline.effective_kw} kW</strong>{' '}
                                    · Wait {recommendation.nearest_baseline.wait_min}m
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
                                    Eff <strong>{recommendation.top3[0].criteria.effective_kw} kW</strong>{' '}
                                    · Wait {recommendation.top3[0].criteria.wait_min}m · Score{' '}
                                    {recommendation.top3[0].score.toFixed(3)}
                                  </span>
                                </div>
                              </div>
                            </section>
                          )}

                          {recommendation && (
                            <section className="panel-section">
                              <div className="results-header">
                                <h3>Top 3 Recommended Stops</h3>
                                <span className="engine-ver">
                                  {recommendation.needs_charging ? 'Charge Needed' : 'Reachable Directly'}
                                </span>
                              </div>

                              {recommendation.top3.length === 0 ? (
                                <p className="muted">
                                  No admissible station met connector + 8% reserve constraints.
                                </p>
                              ) : (
                                <div className="cards-list">
                                  {recommendation.top3.map((st) => (
                                    <div
                                      key={st.station_id}
                                      className={`result-card ${
                                        selectedStation?.properties.station_id === st.station_id
                                          ? 'selected'
                                          : ''
                                      }`}
                                      onClick={() => {
                                        const match = stations.find(
                                          (f) => f.properties.station_id === st.station_id,
                                        )
                                        if (match) setSelectedStation(match)
                                      }}
                                    >
                                      <div className="card-top">
                                        <span className="rank-pill">#{st.rank}</span>
                                        <strong>{st.name}</strong>
                                        <span className="score-pill">{st.score.toFixed(3)}</span>
                                      </div>
                                      <div className="card-metrics">
                                        <span>Eff {st.criteria.effective_kw} kW</span>
                                        <span>Wait {st.criteria.wait_min}m</span>
                                        <span>Arr SoC {st.arrival_soc_pct}%</span>
                                        <span>₹{st.criteria.cost_inr_kwh}/kWh</span>
                                      </div>
                                      <div className="card-metrics">
                                        <span>Detour: +{st.criteria.detour_km} km</span>
                                        <span>Est Cost: ₹{st.est_cost_inr}</span>
                                        <span>Charge: {st.est_charge_min}m</span>
                                        <span className="prov-badge">
                                          {st.source.toUpperCase()} ({Math.round(st.confidence * 100)}%)
                                        </span>
                                      </div>
                                      <div className="explain-list">
                                        {st.explain.slice(0, 2).map((ex, idx) => (
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
                                    {rejectedSummary.breakdown
                                      ? ` (${rejectedSummary.breakdown})`
                                      : ' (Hard Constraints)'}
                                  </summary>
                                  <ul>
                                    {recommendation.rejected.slice(0, 25).map((r) => {
                                      const stName = stationNameById.get(r.station_id)
                                      return (
                                        <li key={r.station_id}>
                                          <strong>
                                            {stName
                                              ? `${stName} (#${r.station_id})`
                                              : `Station #${r.station_id}`}
                                            :
                                          </strong>{' '}
                                          {r.reason}
                                        </li>
                                      )
                                    })}
                                    {recommendation.rejected.length > 25 && (
                                      <li>
                                        <em>
                                          + {recommendation.rejected.length - 25} additional stations
                                          filtered by hard constraints.
                                        </em>
                                      </li>
                                    )}
                                  </ul>
                                </details>
                              )}
                            </section>
                          )}
                        </>
                      )}

                      {drawerTab === 'directions' && (
                        <section className="directions-steps-panel">
                          <div className="directions-summary-banner">
                            <div>
                              <strong className="mono">
                                {routeData ? `${routeData.total_distance_km} km` : `${activePreset.routeKm} km`}
                              </strong>
                              <span>
                                {routeData
                                  ? `${Math.round(routeData.total_duration_min)} min driving (${routeData.provider.toUpperCase()})`
                                  : 'Computing street geometry...'}
                              </span>
                            </div>
                            <button
                              type="button"
                              className={`sim-cta ${simActive ? 'active' : ''}`}
                              onClick={handleToggleSim}
                              disabled={!routeData}
                            >
                              {simActive ? '⏹ Stop' : '▶ Simulate'}
                            </button>
                          </div>

                          {routeData?.legs.map((leg, lIdx) => (
                            <div key={lIdx} className="leg-block">
                              <div className="leg-header">
                                <span className={`leg-badge ${lIdx === 0 ? 'leg1' : 'leg2'}`}>
                                  LEG {lIdx + 1}
                                </span>
                                <strong>
                                  {leg.from_label} → {leg.to_label}
                                </strong>
                                <small className="mono">
                                  {leg.distance_km} km · {Math.round(leg.duration_min)} min
                                </small>
                              </div>
                              <ol className="steps-timeline">
                                {leg.steps.map((step, sIdx) => (
                                  <li
                                    key={sIdx}
                                    className="step-item"
                                    onClick={() => setFocusedStepLoc(step.location)}
                                  >
                                    <span className="step-icon">
                                      {maneuverArrow(step.maneuver_type, step.modifier)}
                                    </span>
                                    <div className="step-body">
                                      <strong>{step.instruction}</strong>
                                      <span className="step-meta">
                                        {step.road_name}
                                        {step.distance_m > 0
                                          ? ` · ${
                                              step.distance_m >= 1000
                                                ? `${(step.distance_m / 1000).toFixed(1)} km`
                                                : `${Math.round(step.distance_m)} m`
                                            }`
                                          : ''}
                                      </span>
                                    </div>
                                  </li>
                                ))}
                              </ol>
                            </div>
                          ))}
                        </section>
                      )}
                    </div>
                  </aside>
                )}
              </>
            )}

            {/* Station Detail Drawer */}
            {selectedStation && !showLanding && (
              <div className="cercos-detail-drawer">
                <button
                  type="button"
                  className="drawer-close"
                  onClick={() => setSelectedStation(null)}
                >
                  ✕
                </button>
                <div className="drawer-badges">
                  <span className="prov-badge">
                    {selectedStation.properties.source.toUpperCase()}
                  </span>
                  <span className="conf-badge">
                    Confidence {Math.round((selectedStation.properties.confidence ?? 0.85) * 100)}%
                  </span>
                </div>
                <h4>{selectedStation.properties.name || selectedStation.properties.station_name}</h4>
                <p className="drawer-addr">{selectedStation.properties.address}</p>
                <div className="drawer-specs">
                  <div>
                    <strong>Operator:</strong>{' '}
                    {selectedStation.properties.cpo_name || 'Public / Unlisted'}
                  </div>
                  <div>
                    <strong>Max Power:</strong> {selectedStation.properties.max_power_kw ?? 'N/A'} kW
                  </div>
                  <div>
                    <strong>Retail Tariff:</strong>{' '}
                    {formatTariff(selectedStation.properties.tariff_inr_kwh)}
                  </div>
                  <div>
                    <strong>Hours:</strong> {selectedStation.properties.hours_text || '24/7'}
                  </div>
                  <div>
                    <strong>Registry Ref:</strong>{' '}
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

            {/* Google Maps-inspired Hero Landing Sheet over Live Map */}
            <LandingOverlay
              visible={showLanding}
              stationCount={stations.length}
              statusInfo={statusInfo}
              presets={CORRIDOR_PRESETS}
              onLaunchNavigator={() => setShowLanding(false)}
              onSelectCorridor={handleSelectCorridorFromLanding}
              onOpenAudit={() => {
                setShowLanding(false)
                setActiveTab('audit')
              }}
            />
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
            <h3>Real Data Provenance &amp; System Verification</h3>
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
                    {statusInfo.policy_benchmarks?.mhi_rajya_sabha_q3910_2026_03_27
                      ?.omc_stations_operational ?? 1291}{' '}
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
                      setShowLanding(false)
                      setActiveTab('map')
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>{s.properties.station_id}</td>
                    <td>{s.properties.name || s.properties.station_name}</td>
                    <td>{s.properties.cpo_name || 'Public / Unlisted'}</td>
                    <td className="mono">
                      {s.geometry.coordinates[1].toFixed(4)}, {s.geometry.coordinates[0].toFixed(4)}
                    </td>
                    <td>{s.properties.max_power_kw ?? 'N/A'} kW</td>
                    <td>{formatTariff(s.properties.tariff_inr_kwh)}</td>
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

      {/* Sticky Mobile App Bottom Navigation Bar */}
      <nav className="mobile-bottom-nav" aria-label="Mobile Navigation">
        <button
          type="button"
          className={`m-nav-btn ${activeTab === 'map' && showLanding ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('map')
            setShowLanding(true)
          }}
        >
          <span>✨</span>
          <small>Overview</small>
        </button>
        <button
          type="button"
          className={`m-nav-btn ${activeTab === 'map' && !showLanding ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('map')
            setShowLanding(false)
          }}
        >
          <span>🗺️</span>
          <small>Explore</small>
        </button>
        <button
          type="button"
          className={`m-nav-btn ${activeTab === 'field' ? 'active' : ''}`}
          onClick={() => {
            setShowLanding(false)
            setActiveTab('field')
          }}
        >
          <span>📋</span>
          <small>Field</small>
        </button>
        <button
          type="button"
          className={`m-nav-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => {
            setShowLanding(false)
            setActiveTab('audit')
          }}
        >
          <span>📊</span>
          <small>Audit</small>
        </button>
      </nav>
    </div>
  )
}

export default App
