import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import gsap from 'gsap'
import { useGSAP } from '@gsap/react'
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
    label: 'Bhopal → Indore (~195 km)',
    originLabel: 'Bhopal Central',
    destLabel: 'Indore (Rajwada / AB Rd)',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 22.7196, lon: 75.8577 },
    routeKm: 195.0,
  },
  {
    id: 'bhopal-sehore',
    label: 'Bhopal → VIT Bhopal (~45 km)',
    originLabel: 'Bhopal City',
    destLabel: 'VIT Bhopal (Kothri Kalan)',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 23.074, lon: 76.8298 },
    routeKm: 45.0,
  },
  {
    id: 'bhopal-vidisha',
    label: 'Bhopal → Vidisha (~58 km)',
    originLabel: 'Bhopal Junction',
    destLabel: 'Vidisha Town',
    origin: { lat: 23.2599, lon: 77.4126 },
    destination: { lat: 23.5226, lon: 77.8148 },
    routeKm: 58.0,
  },
  {
    id: 'bhopal-urban',
    label: 'Bhopal Urban Loop (~22 km)',
    originLabel: 'MP Nagar Zone 1',
    destLabel: 'Bairagarh / Bhojtal West',
    origin: { lat: 23.2338, lon: 77.4319 },
    destination: { lat: 23.2712, lon: 77.3385 },
    routeKm: 22.0,
  },
]

const ALL_MP_BBOX = '75.0,22.0,79.0,24.5'

interface PlaceOption {
  id: string
  label: string
  subtitle: string
  lat: number
  lon: number
}

const MP_LANDMARKS: PlaceOption[] = [
  { id: 'lm-bhopal-jn', label: 'Bhopal Junction Railway Station', subtitle: 'Bhopal, Madhya Pradesh', lat: 23.2689, lon: 77.4136 },
  { id: 'lm-rkmp', label: 'Rani Kamalapati (Habibganj) Station', subtitle: 'MP Nagar, Bhopal', lat: 23.2295, lon: 77.4391 },
  { id: 'lm-db-mall', label: 'DB City Mall, Bhopal', subtitle: 'Arera Hills, Bhopal', lat: 23.2332, lon: 77.4301 },
  { id: 'lm-airport', label: 'Raja Bhoj Airport, Bhopal', subtitle: 'Gandhi Nagar, Bhopal', lat: 23.2875, lon: 77.3374 },
  { id: 'lm-vit-bhopal', label: 'VIT Bhopal University', subtitle: 'Kothri Kalan, Sehore', lat: 23.0775, lon: 76.8513 },
  { id: 'lm-sehore', label: 'Sehore Town / NH-46', subtitle: 'Sehore, Madhya Pradesh', lat: 23.2032, lon: 77.0844 },
  { id: 'lm-ashta', label: 'Ashta Highway Interchange', subtitle: 'Ashta, Sehore', lat: 23.0195, lon: 76.7222 },
  { id: 'lm-dewas', label: 'Dewas AB Road Corridor', subtitle: 'Dewas, Madhya Pradesh', lat: 22.9676, lon: 76.0534 },
  { id: 'lm-indore-vn', label: 'Vijay Nagar Square, Indore', subtitle: 'Indore, Madhya Pradesh', lat: 22.7533, lon: 75.8937 },
  { id: 'lm-indore-raj', label: 'Rajwada, Indore', subtitle: 'Central Indore', lat: 22.7186, lon: 75.8548 },
  { id: 'lm-vidisha', label: 'Vidisha Town Center', subtitle: 'Vidisha, Madhya Pradesh', lat: 23.5226, lon: 77.8148 },
  { id: 'lm-ujjain', label: 'Ujjain Mahakal Corridor', subtitle: 'Ujjain, Madhya Pradesh', lat: 23.1828, lon: 75.7682 },
]

function haversineKm(a: LatLon, b: LatLon): number {
  const toRad = (deg: number) => (deg * Math.PI) / 180
  const dLat = toRad(b.lat - a.lat)
  const dLon = toRad(b.lon - a.lon)
  const lat1 = toRad(a.lat)
  const lat2 = toRad(b.lat)
  const h =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) * Math.sin(dLon / 2)
  return 6371 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h))
}

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
  const appRef = useRef<HTMLDivElement>(null)

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

  // User live location
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null)
  const [locationError, setLocationError] = useState<string | null>(null)

  // Search bar & custom origin/destination
  const [searchOrigin, setSearchOrigin] = useState<string>('')
  const [searchDest, setSearchDest] = useState<string>('')
  const [customOrigin, setCustomOrigin] = useState<{ lat: number; lon: number; label: string } | null>(null)
  const [customDest, setCustomDest] = useState<{ lat: number; lon: number; label: string } | null>(null)
  const [activeSearchField, setActiveSearchField] = useState<'origin' | 'dest' | null>(null)
  const [remotePlaces, setRemotePlaces] = useState<PlaceOption[]>([])
  const [searchingPlaces, setSearchingPlaces] = useState<boolean>(false)

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

  const effectiveOrigin = useMemo<LatLon>(
    () => (customOrigin ? { lat: customOrigin.lat, lon: customOrigin.lon } : activePreset.origin),
    [customOrigin, activePreset],
  )

  const effectiveDest = useMemo<LatLon>(
    () => (customDest ? { lat: customDest.lat, lon: customDest.lon } : activePreset.destination),
    [customDest, activePreset],
  )

  const effectiveOriginLabel = customOrigin ? customOrigin.label : activePreset.originLabel
  const effectiveDestLabel = customDest ? customDest.label : activePreset.destLabel

  const effectiveRouteKm = useMemo(() => {
    if (!customOrigin && !customDest) return activePreset.routeKm
    return Math.max(4, Math.round(haversineKm(effectiveOrigin, effectiveDest) * 1.25))
  }, [customOrigin, customDest, activePreset.routeKm, effectiveOrigin, effectiveDest])

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
    if (mismatch > 0) parts.push(`${mismatch} wrong plug`)
    if (unreachable > 0) parts.push(`${unreachable} too far`)
    if (offline > 0) parts.push(`${offline} offline`)
    return {
      total: list.length,
      breakdown: parts.join(' · '),
    }
  }, [recommendation])

  // ───── Live Location ─────
  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported in this browser')
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude
        const lon = pos.coords.longitude
        setUserLocation([lat, lon])
        setCustomOrigin({ lat, lon, label: 'My Live Location' })
        setSearchOrigin('My Live Location')
        setLocationError(null)
        setActiveSearchField(null)
        setRecommendation(null)
      },
      (err) => {
        setLocationError(err.message || 'Location permission denied')
      },
      { enableHighAccuracy: true, timeout: 10000 },
    )
  }, [])

  // Debounced Nominatim place search when user types in Origin or Where To
  const activeQuery = activeSearchField === 'origin' ? searchOrigin : activeSearchField === 'dest' ? searchDest : ''
  useEffect(() => {
    const q = activeQuery.trim()
    if (!activeSearchField || q.length < 3 || q === 'My Live Location') {
      setRemotePlaces([])
      setSearchingPlaces(false)
      return
    }
    const controller = new AbortController()
    const timer = window.setTimeout(async () => {
      setSearchingPlaces(true)
      try {
        const url = `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(q)}&countrycodes=in&limit=5`
        const resp = await fetch(url, {
          signal: controller.signal,
          headers: { Accept: 'application/json' },
        })
        if (!resp.ok) {
          setRemotePlaces([])
          return
        }
        const rows = (await resp.json()) as Array<{
          place_id: number
          display_name: string
          lat: string
          lon: string
        }>
        setRemotePlaces(
          rows.map((r) => {
            const parts = r.display_name.split(',').map((s) => s.trim())
            return {
              id: `nom-${r.place_id}`,
              label: parts[0] || r.display_name,
              subtitle: parts.slice(1, 4).join(', '),
              lat: Number(r.lat),
              lon: Number(r.lon),
            }
          }),
        )
      } catch {
        setRemotePlaces([])
      } finally {
        setSearchingPlaces(false)
      }
    }, 350)
    return () => {
      window.clearTimeout(timer)
      controller.abort()
    }
  }, [activeQuery, activeSearchField])

  const filteredLandmarks = useMemo(() => {
    const q = activeQuery.trim().toLowerCase()
    if (!q || q === 'my live location') return MP_LANDMARKS.slice(0, 6)
    return MP_LANDMARKS.filter(
      (lm) => lm.label.toLowerCase().includes(q) || lm.subtitle.toLowerCase().includes(q),
    ).slice(0, 6)
  }, [activeQuery])

  // ───── Data Loading ─────
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
        origin: effectiveOrigin,
        destination: effectiveDest,
        soc_pct: socPct,
        mode: selectedMode as
          | 'Balanced'
          | 'Cheapest'
          | 'Fastest'
          | 'Shortest'
          | 'HighestRated'
          | 'BatterySafe',
        segment: veh?.segment || 'E4W',
        vehicle_id: veh?.vehicle_id,
        vehicle_model: veh?.model_name,
        route_km: effectiveRouteKm,
      })
      setRecommendation(res)

      const top1 = res.top3[0]
      if (top1) {
        const match = stations.find((s) => s.properties.station_id === top1.station_id)
        if (match) setSelectedStation(match)
      }

      const routeRes = await cercosApi
        .getRoute({
          origin: effectiveOrigin,
          destination: effectiveDest,
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
  }, [vehicles, selectedVehicleIdx, effectiveOrigin, effectiveDest, effectiveRouteKm, socPct, selectedMode, stations])

  useEffect(() => {
    if (stations.length > 0 && vehicles.length > 0 && !recommendation && !useMocks) {
      runOptimize()
    }
  }, [stations.length, vehicles.length, recommendation, useMocks, runOptimize])

  // Flatten route coords & steps for Drive Preview
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
    setCustomOrigin(null)
    setCustomDest(null)
    setSearchOrigin('')
    setSearchDest('')
    setRecommendation(null)
    setShowLanding(false)
    setActiveTab('map')
    setPanelCollapsed(false)
    setDrawerTab('directions')
  }

  const handleSelectPreset = (presetId: string) => {
    setSelectedPresetId(presetId)
    setCustomOrigin(null)
    setCustomDest(null)
    setSearchOrigin('')
    setSearchDest('')
    setActiveSearchField(null)
    setRecommendation(null)
  }

  const handleSelectPlace = (place: PlaceOption) => {
    const field = activeSearchField || 'dest'
    if (field === 'origin') {
      setCustomOrigin({ lat: place.lat, lon: place.lon, label: place.label })
      setSearchOrigin(place.label)
    } else {
      setCustomDest({ lat: place.lat, lon: place.lon, label: place.label })
      setSearchDest(place.label)
    }
    setActiveSearchField(null)
    setRecommendation(null)
  }

  const handleSwapEndpoints = () => {
    const prevOrig = { lat: effectiveOrigin.lat, lon: effectiveOrigin.lon, label: effectiveOriginLabel }
    const prevDest = { lat: effectiveDest.lat, lon: effectiveDest.lon, label: effectiveDestLabel }
    setCustomOrigin(prevDest)
    setCustomDest(prevOrig)
    setSearchOrigin(prevDest.label)
    setSearchDest(prevOrig.label)
    setRecommendation(null)
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

  // GSAP entrance animation for the app header
  useGSAP(
    () => {
      if (!appRef.current) return
      gsap.fromTo(
        '.cercos-brand',
        { x: -20, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.5, ease: 'power2.out' },
      )
      gsap.fromTo(
        '.nav-btn',
        { y: -10, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.3, stagger: 0.06, ease: 'power2.out', delay: 0.2 },
      )
    },
    { scope: appRef },
  )

  return (
    <div className="cercos-app" ref={appRef}>
      <MockBanner visible={useMocks} />

      {/* ───── Header ───── */}
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
            Navigator
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
            Audit
          </button>
        </nav>

        <div className="cercos-header-meta">
          <span className={`cercos-badge ${statusInfo?.database.connected ? 'badge-live' : ''}`}>
            {statusInfo?.database.connected
              ? `Live · ${stations.length} Stations`
              : `${stations.length} Loaded`}
          </span>
        </div>
      </header>

      {apiError && (
        <div className="cercos-error-bar">
          <strong>Backend:</strong> {apiError} — ensure FastAPI is running on{' '}
          <code>http://localhost:8000</code>.
        </div>
      )}

      {/* ───── Map Tab ───── */}
      {activeTab === 'map' && (
        <main className="cercos-workspace">
          <div className="cercos-map-pane">
            <MapView
              stations={stations}
              recommendation={recommendation}
              routeData={routeData}
              origin={effectiveOrigin}
              destination={effectiveDest}
              selectedStationId={selectedStation?.properties.station_id ?? null}
              focusedStepLoc={focusedStepLoc}
              simActive={simActive}
              simPosition={simPosition}
              simStep={simStep}
              userLocation={userLocation}
              activeVehicle={activeVehicle}
              onToggleSim={routeData ? handleToggleSim : undefined}
              onSelectStation={(st) => setSelectedStation(st)}
              onOpenLanding={() => setShowLanding(true)}
            />

            {/* Google Maps Left Dock: Floating Search Bar + Directions Drawer */}
            {!showLanding && (
              <div className="gmaps-left-overlay">
                <div className="gmaps-search-bar">
                  <div className="search-route-inputs">
                    <div className="search-dot-col">
                      <span className="search-dot origin-dot" />
                      <span className="search-line" />
                      <span className="search-dot dest-dot" />
                    </div>
                    <div className="search-fields">
                      <div className="search-input-wrap">
                        <input
                          type="text"
                          className="search-input"
                          aria-label="Origin location"
                          placeholder="Your location or starting point"
                          value={searchOrigin || effectiveOriginLabel}
                          onChange={(e) => {
                            setSearchOrigin(e.target.value)
                            setActiveSearchField('origin')
                          }}
                          onFocus={() => setActiveSearchField('origin')}
                        />
                        <button
                          type="button"
                          className={`search-loc-btn ${userLocation ? 'active' : ''}`}
                          onClick={requestLocation}
                          title="Use my live GPS location"
                          aria-label="Use my live location"
                        >
                          📍
                        </button>
                      </div>
                      <div className="search-input-wrap">
                        <input
                          type="text"
                          className="search-input"
                          aria-label="Destination location"
                          placeholder="Where to? (e.g. VIT Bhopal, Indore...)"
                          value={searchDest || effectiveDestLabel}
                          onChange={(e) => {
                            setSearchDest(e.target.value)
                            setActiveSearchField('dest')
                          }}
                          onFocus={() => setActiveSearchField('dest')}
                        />
                        <button
                          type="button"
                          className="search-swap-btn"
                          onClick={handleSwapEndpoints}
                          title="Swap origin and destination"
                          aria-label="Swap origin and destination"
                        >
                          ⇅
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Quick Place & Corridor Suggestions Dropdown */}
                  {activeSearchField && (
                    <div className="search-suggestions">
                      {activeSearchField === 'origin' && (
                        <button
                          type="button"
                          className="search-suggestion-item live-gps-choice"
                          onClick={requestLocation}
                        >
                          <span className="suggestion-icon">📡</span>
                          <div className="suggestion-info">
                            <strong>Use My Live GPS Location</strong>
                            <span>Automatically detect current coordinates</span>
                          </div>
                          <span className="suggestion-km">GPS</span>
                        </button>
                      )}

                      {searchingPlaces && (
                        <div className="search-loading-row">Searching exact locations on map...</div>
                      )}

                      {remotePlaces.length > 0 && (
                        <>
                          <div className="search-suggestions-header">Exact Map Results</div>
                          {remotePlaces.map((pl) => (
                            <button
                              key={pl.id}
                              type="button"
                              className="search-suggestion-item"
                              onClick={() => handleSelectPlace(pl)}
                            >
                              <span className="suggestion-icon">📍</span>
                              <div className="suggestion-info">
                                <strong>{pl.label}</strong>
                                <span>{pl.subtitle}</span>
                              </div>
                            </button>
                          ))}
                        </>
                      )}

                      <div className="search-suggestions-header">
                        MP Landmarks ({activeSearchField === 'origin' ? 'Set Start' : 'Set Destination'})
                      </div>
                      {filteredLandmarks.map((lm) => (
                        <button
                          key={lm.id}
                          type="button"
                          className="search-suggestion-item"
                          onClick={() => handleSelectPlace(lm)}
                        >
                          <span className="suggestion-icon">🏁</span>
                          <div className="suggestion-info">
                            <strong>{lm.label}</strong>
                            <span>{lm.subtitle}</span>
                          </div>
                        </button>
                      ))}

                      <div className="search-suggestions-header">Popular EV Corridors</div>
                      {CORRIDOR_PRESETS.map((p) => (
                        <button
                          key={p.id}
                          type="button"
                          className={`search-suggestion-item ${
                            !customOrigin && !customDest && selectedPresetId === p.id ? 'active' : ''
                          }`}
                          onClick={() => handleSelectPreset(p.id)}
                        >
                          <span className="suggestion-icon">🛣️</span>
                          <div className="suggestion-info">
                            <strong>{p.label}</strong>
                            <span>
                              {p.originLabel} → {p.destLabel}
                            </span>
                          </div>
                          <span className="suggestion-km mono">{p.routeKm} km</span>
                        </button>
                      ))}
                      <button
                        type="button"
                        className="search-close-btn"
                        onClick={() => setActiveSearchField(null)}
                      >
                        Close
                      </button>
                    </div>
                  )}

                  {/* Vehicle + SoC compact strip below search */}
                  {activeVehicle && (
                    <div className="search-vehicle-strip">
                      <span className="vehicle-chip">
                        🚗 {activeVehicle.model_name} · {socPct}% SoC
                      </span>
                      <span className="range-chip mono">
                        ~{recommendation?.reachable_km ?? reachableEstimateKm} km range
                      </span>
                    </div>
                  )}

                  {locationError && (
                    <div className="location-error">
                      📍 {locationError}
                    </div>
                  )}
                </div>

                {panelCollapsed ? (
                  <button
                    type="button"
                    className="floating-expand-pill"
                    onClick={() => setPanelCollapsed(false)}
                  >
                    🧭 Directions ({recommendation?.top3.length ?? 0})
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
                          {recommendation?.top3[0]?.name || `${effectiveOriginLabel} → ${effectiveDestLabel}`}
                        </strong>
                        <span className="mono">
                          {routeData
                            ? `${routeData.total_distance_km} km · ${Math.round(routeData.total_duration_min)}m`
                            : `${effectiveRouteKm} km`}
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
                          Route Setup
                        </button>
                        <button
                          type="button"
                          className={`d-tab ${drawerTab === 'directions' ? 'active' : ''}`}
                          onClick={() => setDrawerTab('directions')}
                        >
                          Directions ({simSteps.length})
                        </button>
                      </div>
                      <button
                        type="button"
                        className="collapse-drawer-btn"
                        onClick={() => setPanelCollapsed(true)}
                        title="Hide Panel"
                      >
                        ◀
                      </button>
                    </div>

                    <div className="drawer-scroll-body">
                      {/* Route Box */}
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
                            <strong>{effectiveOriginLabel}</strong>
                          </div>
                          <div className="route-row-pill stop-pill">
                            <small>OPTIMAL CHARGE STOP</small>
                            <strong>
                              {recommendation?.top3[0]?.name || 'Computing best stop...'}
                            </strong>
                          </div>
                          <div className="route-row-pill">
                            <small>DESTINATION</small>
                            <strong>{effectiveDestLabel}</strong>
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
                                onChange={(e) => handleSelectPreset(e.target.value)}
                              >
                                {CORRIDOR_PRESETS.map((p) => (
                                  <option key={p.id} value={p.id}>
                                    {p.label}
                                  </option>
                                ))}
                              </select>
                            </label>

                            <label className="field-label">
                              Vehicle
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
                              Battery: <strong>{socPct}%</strong> · Range:{' '}
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
                                {loadingRec ? 'Routing...' : '⚡ Find Best Stop'}
                              </button>
                              {routeData && (
                                <button
                                  type="button"
                                  className={`sim-cta ${simActive ? 'active' : ''}`}
                                  onClick={handleToggleSim}
                                >
                                  {simActive ? '⏹ Stop' : '▶ Preview'}
                                </button>
                              )}
                            </div>
                          </section>

                          {/* Comparison Card */}
                          {recommendation?.nearest_baseline && recommendation.top3.length > 0 && (
                            <section className="panel-section comparison-card">
                              <h4>Nearest vs CERCOS #1</h4>
                              <div className="compare-grid">
                                <div className="compare-col baseline">
                                  <span className="col-tag">Nearest</span>
                                  <strong>{recommendation.nearest_baseline.name}</strong>
                                  <span>
                                    ₹{recommendation.nearest_baseline.tariff_inr_kwh}/kWh ·{' '}
                                    {recommendation.nearest_baseline.is_compatible
                                      ? '✓ Plug OK'
                                      : '⚠ Wrong Plug'}
                                  </span>
                                </div>
                                <div className="compare-col cercos">
                                  <span className="col-tag win">★ CERCOS</span>
                                  <strong>{recommendation.top3[0].name}</strong>
                                  <span>
                                    ₹{recommendation.top3[0].criteria.cost_inr_kwh}/kWh ·{' '}
                                    {recommendation.nearest_baseline.cost_diff_vs_cercos_inr_kwh >= 0
                                      ? `Saves ₹${recommendation.nearest_baseline.cost_diff_vs_cercos_inr_kwh}`
                                      : `+₹${Math.abs(recommendation.nearest_baseline.cost_diff_vs_cercos_inr_kwh)}`}
                                  </span>
                                </div>
                              </div>
                            </section>
                          )}

                          {/* Top 3 Results */}
                          {recommendation && (
                            <section className="panel-section">
                              <div className="results-header">
                                <h3>Top 3 Stops</h3>
                                <span className="engine-ver">
                                  {recommendation.needs_charging ? 'Charge Needed' : 'Direct OK'}
                                </span>
                              </div>

                              {recommendation.top3.length === 0 ? (
                                <p className="muted">
                                  No station met plug + 8% reserve constraints.
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
                                        <span>SoC {st.arrival_soc_pct}%</span>
                                        <span>₹{st.criteria.cost_inr_kwh}/kWh</span>
                                      </div>
                                      <div className="card-metrics">
                                        <span>+{st.criteria.detour_km} km detour</span>
                                        <span>₹{st.est_cost_inr} est</span>
                                        <span>{st.est_charge_min}m charge</span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              )}

                              {/* Incompatible stations summary */}
                              {recommendation.rejected.length > 0 && (
                                <details className="rejected-details">
                                  <summary>
                                    <span className="rejected-count">{rejectedSummary.total}</span>{' '}
                                    stations filtered
                                    {rejectedSummary.breakdown
                                      ? ` — ${rejectedSummary.breakdown}`
                                      : ''}
                                  </summary>
                                  <div className="rejected-list">
                                    {recommendation.rejected.slice(0, 15).map((r) => {
                                      const stName = stationNameById.get(r.station_id)
                                      const lower = r.reason.toLowerCase()
                                      const icon = lower.includes('connector') ? '🔌' : lower.includes('unreachable') ? '🔋' : '✕'
                                      return (
                                        <div key={r.station_id} className="rejected-item">
                                          <span className="rejected-icon">{icon}</span>
                                          <div>
                                            <strong>{stName || `Station #${r.station_id}`}</strong>
                                            <span className="rejected-reason">
                                              {lower.includes('connector mismatch')
                                                ? `This station won't work with your ${activeVehicle?.model_name || 'vehicle'}`
                                                : lower.includes('unreachable')
                                                  ? 'Too far for current battery'
                                                  : r.reason}
                                            </span>
                                          </div>
                                        </div>
                                      )
                                    })}
                                    {recommendation.rejected.length > 15 && (
                                      <div className="rejected-more">
                                        +{recommendation.rejected.length - 15} more filtered
                                      </div>
                                    )}
                                  </div>
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
                                {routeData ? `${routeData.total_distance_km} km` : `${effectiveRouteKm} km`}
                              </strong>
                              <span>
                                {routeData
                                  ? `${Math.round(routeData.total_duration_min)} min (${routeData.provider.toUpperCase()})`
                                  : 'Computing...'}
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
              </div>
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
                    {Math.round((selectedStation.properties.confidence ?? 0.85) * 100)}% conf
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
                    <strong>Power:</strong> {selectedStation.properties.max_power_kw ?? 'N/A'} kW
                  </div>
                  <div>
                    <strong>Tariff:</strong>{' '}
                    {formatTariff(selectedStation.properties.tariff_inr_kwh)}
                  </div>
                  <div>
                    <strong>Hours:</strong> {selectedStation.properties.hours_text || '24/7'}
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

            {/* Landing Overlay */}
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

      {/* ───── Field Tab ───── */}
      {activeTab === 'field' && (
        <main className="cercos-page-grid">
          <div className="page-card">
            <h3>Station Hardware Census</h3>
            <p className="muted">
              Persisted to CERCOS database via <code>POST /v1/field/census</code>.
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
            <h3>Anonymous Driver BWM Survey</h3>
            <p className="muted">
              Consent required. Zero names or phone numbers stored.
            </p>
            <form onSubmit={handleSurveySubmit} className="cercos-form">
              <label className="consent-box">
                <input
                  type="checkbox"
                  checked={surveyConsent}
                  onChange={(e) => setSurveyConsent(e.target.checked)}
                />
                <span>Participant gave informed verbal consent.</span>
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
                  <option value="E3W">Electric Three-Wheeler (E3W)</option>
                  <option value="E4W">Electric Four-Wheeler (E4W)</option>
                  <option value="ELCV">Electric LCV (ELCV)</option>
                </select>
              </label>
              <div className="form-row">
                <label className="field-label">
                  Most Important
                  <select value={surveyBest} onChange={(e) => setSurveyBest(e.target.value)}>
                    <option value="cost">Charging Cost</option>
                    <option value="wait">Queue Wait</option>
                    <option value="detour">Detour Distance</option>
                    <option value="speed">Charging Speed</option>
                    <option value="soc">Battery Safety</option>
                  </select>
                </label>
                <label className="field-label">
                  Least Important
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
              <strong>CSV Exports:</strong>
              <div className="export-links">
                <a href={cercosApi.getExportUrl('census')} target="_blank" rel="noreferrer">
                  Census
                </a>
                <a href={cercosApi.getExportUrl('survey')} target="_blank" rel="noreferrer">
                  Survey
                </a>
                <a href={cercosApi.getExportUrl('queue')} target="_blank" rel="noreferrer">
                  Queue
                </a>
              </div>
            </div>
          </div>
        </main>
      )}

      {/* ───── Audit Tab ───── */}
      {activeTab === 'audit' && (
        <main className="cercos-page-grid single">
          <div className="page-card">
            <h3>Real Data Provenance & System Verification</h3>
            {statusInfo && (
              <div className="audit-stats">
                <div className="stat-box">
                  <span className="stat-lbl">Database</span>
                  <strong>{statusInfo.database.backend}</strong>
                </div>
                <div className="stat-box">
                  <span className="stat-lbl">Active Stations</span>
                  <strong>{statusInfo.stations_total}</strong>
                </div>
                <div className="stat-box">
                  <span className="stat-lbl">MHI Official</span>
                  <strong>
                    {statusInfo.policy_benchmarks?.mhi_rajya_sabha_q3910_2026_03_27
                      ?.omc_stations_operational ?? 1291}{' '}
                    / 1,417
                  </strong>
                </div>
                <div className="stat-box">
                  <span className="stat-lbl">Highway Spacing</span>
                  <strong>25 km Max</strong>
                </div>
              </div>
            )}

            <table className="audit-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Station</th>
                  <th>Operator</th>
                  <th>Coords</th>
                  <th>kW</th>
                  <th>Tariff</th>
                  <th>Source</th>
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
                    <td>{s.properties.cpo_name || 'Public'}</td>
                    <td className="mono">
                      {s.geometry.coordinates[1].toFixed(4)}, {s.geometry.coordinates[0].toFixed(4)}
                    </td>
                    <td>{s.properties.max_power_kw ?? 'N/A'}</td>
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

      {/* ───── Mobile Bottom Nav ───── */}
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
          <small>Navigate</small>
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
