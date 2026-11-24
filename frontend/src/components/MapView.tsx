import React, { useEffect, useMemo, useState } from 'react'
import {
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  Tooltip,
  useMap,
} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  formatTariff,
  type LatLon,
  type NearestBaselineComparison,
  type RecommendResult,
  type RouteResponse,
  type RouteStep,
  type StationFeature,
} from '../api/client'

const BHOPAL_CENTER: [number, number] = [23.2599, 77.4126]
const DEFAULT_ZOOM = 11

type MapFilterMode = 'all' | 'recommended' | 'fast' | 'light_ev'

export interface MapViewProps {
  center?: [number, number]
  zoom?: number
  stations?: StationFeature[]
  recommendation?: RecommendResult | null
  routeData?: RouteResponse | null
  origin?: LatLon | null
  destination?: LatLon | null
  selectedStationId?: number | null
  focusedStepLoc?: [number, number] | null
  simActive?: boolean
  simPosition?: [number, number] | null
  simStep?: RouteStep | null
  onToggleSim?: () => void
  onSelectStation?: (station: StationFeature) => void
  onOpenLanding?: () => void
}

function createPinIcon(options: {
  bg: string
  border: string
  label: string
  size?: number
  pulse?: boolean
  selected?: boolean
}): L.DivIcon {
  const size = options.size ?? 30
  const ring = options.selected
    ? 'box-shadow: 0 0 0 4px rgba(255,255,255,0.98), 0 0 18px rgba(26,115,232,0.9);'
    : 'box-shadow: 0 3px 8px rgba(15,23,42,0.35);'
  const pulseClass = options.pulse ? 'cercos-pin-pulse' : ''

  return L.divIcon({
    className: `cercos-custom-pin ${pulseClass}`,
    html: `<div style="
      width:${size}px;
      height:${size}px;
      border-radius:9999px;
      background:${options.bg};
      border:2.5px solid ${options.border};
      color:#ffffff;
      font-weight:800;
      font-size:${size > 32 ? '11.5px' : '9.5px'};
      display:flex;
      align-items:center;
      justify-content:center;
      ${ring}
    ">${options.label}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -(size / 2 + 4)],
  })
}

const endpointIcon = (label: string, bg: string) =>
  L.divIcon({
    className: 'cercos-endpoint-pin',
    html: `<div style="
      padding:4px 9px;
      border-radius:9999px;
      background:${bg};
      color:#fff;
      font-weight:700;
      font-size:11px;
      border:2px solid #fff;
      box-shadow:0 4px 12px rgba(15,23,42,0.38);
      white-space:nowrap;
    ">${label}</div>`,
    iconSize: [78, 26],
    iconAnchor: [39, 13],
  })

const navPuckIcon = () =>
  L.divIcon({
    className: 'cercos-nav-puck',
    html: `<div class="nav-puck-outer"><div class="nav-puck-core">▲</div></div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  })

const MapViewportController: React.FC<{
  stations: StationFeature[]
  selectedStation?: StationFeature | null
  focusedStepLoc?: [number, number] | null
  simPosition?: [number, number] | null
  origin?: LatLon | null
  destination?: LatLon | null
  fitTrigger: number
}> = ({
  stations,
  selectedStation,
  focusedStepLoc,
  simPosition,
  origin,
  destination,
  fitTrigger,
}) => {
  const map = useMap()

  useEffect(() => {
    if (!selectedStation) return
    const [lon, lat] = selectedStation.geometry.coordinates
    try {
      map.flyTo([lat, lon], Math.max(map.getZoom(), 13), { duration: 0.65 })
    } catch {
      // Ignore inside jsdom tests without layout geometry
    }
  }, [map, selectedStation])

  useEffect(() => {
    if (!focusedStepLoc) return
    try {
      map.flyTo(focusedStepLoc, 14, { duration: 0.6 })
    } catch {
      // Ignore in test runtime
    }
  }, [map, focusedStepLoc])

  useEffect(() => {
    if (!simPosition) return
    try {
      map.panTo(simPosition, { animate: true, duration: 0.25 })
    } catch {
      // Ignore in test runtime
    }
  }, [map, simPosition])

  useEffect(() => {
    const pts: [number, number][] = []
    if (origin) pts.push([origin.lat, origin.lon])
    if (destination) pts.push([destination.lat, destination.lon])
    if (pts.length === 0) {
      stations.forEach((s) => pts.push([s.geometry.coordinates[1], s.geometry.coordinates[0]]))
    }
    if (pts.length >= 2) {
      try {
        map.fitBounds(L.latLngBounds(pts), { padding: [55, 55], maxZoom: 12 })
      } catch {
        // Ignore in headless test runtime
      }
    }
  }, [map, origin, destination, fitTrigger, stations])

  return null
}

export const MapView: React.FC<MapViewProps> = ({
  center = BHOPAL_CENTER,
  zoom = DEFAULT_ZOOM,
  stations = [],
  recommendation = null,
  routeData = null,
  origin = null,
  destination = null,
  selectedStationId = null,
  focusedStepLoc = null,
  simActive = false,
  simPosition = null,
  simStep = null,
  onToggleSim,
  onSelectStation,
  onOpenLanding,
}) => {
  const [filterMode, setFilterMode] = useState<MapFilterMode>('all')
  const [fitTrigger, setFitTrigger] = useState(0)
  const [legendExpanded, setLegendExpanded] = useState(false)

  const rankByStationId = useMemo(() => {
    const map = new Map<number, number>()
    recommendation?.top3.forEach((item) => {
      map.set(item.station_id, item.rank)
    })
    return map
  }, [recommendation])

  const rejectedReasons = useMemo(() => {
    const map = new Map<number, string>()
    recommendation?.rejected.forEach((r) => {
      map.set(r.station_id, r.reason)
    })
    return map
  }, [recommendation])

  const nearestBaseline: NearestBaselineComparison | null | undefined =
    recommendation?.nearest_baseline

  const filteredStations = useMemo(() => {
    return stations.filter((st) => {
      const id = st.properties.station_id
      const kw = st.properties.max_power_kw ?? 0
      const conns = st.properties.connector_types ?? []

      if (filterMode === 'recommended') return rankByStationId.has(id)
      if (filterMode === 'fast') return kw >= 50
      if (filterMode === 'light_ev')
        return (
          conns.includes('LECCS') ||
          conns.includes('15A_Socket') ||
          conns.includes('Type2') ||
          kw <= 22
        )
      return true
    })
  }, [stations, filterMode, rankByStationId])

  const isJsdom = typeof navigator !== 'undefined' && /jsdom/i.test(navigator.userAgent)

  const selectedStation = useMemo(
    () => stations.find((s) => s.properties.station_id === selectedStationId) ?? null,
    [stations, selectedStationId],
  )

  const top1Station = recommendation?.top3[0]
  const fallbackCoords: [number, number][] = useMemo(() => {
    if (!origin || !destination) return []
    if (top1Station && top1Station.lat != null && top1Station.lon != null) {
      return [
        [origin.lat, origin.lon],
        [top1Station.lat, top1Station.lon],
        [destination.lat, destination.lon],
      ]
    }
    return [
      [origin.lat, origin.lon],
      [destination.lat, destination.lon],
    ]
  }, [origin, destination, top1Station])

  const leg1Coords = routeData?.legs[0]?.coordinates ?? fallbackCoords
  const leg2Coords = routeData?.legs[1]?.coordinates ?? []

  return (
    <div
      data-testid="map-container"
      className="cercos-map-wrapper"
      style={{ width: '100%', height: '100%', position: 'relative', minHeight: '340px' }}
    >
      {/* Google Maps-style Live Turn-by-Turn Navigation HUD Banner during Preview */}
      {simActive && simStep && (
        <div className="gmaps-turn-hud" role="status" aria-live="polite">
          <div className="turn-hud-icon">↱</div>
          <div className="turn-hud-text">
            <strong>{simStep.instruction}</strong>
            <span>
              {simStep.road_name} ·{' '}
              {simStep.distance_m >= 1000
                ? `${(simStep.distance_m / 1000).toFixed(1)} km`
                : `${Math.round(simStep.distance_m)} m`}
            </span>
          </div>
          {onToggleSim && (
            <button type="button" className="turn-hud-stop" onClick={onToggleSim}>
              Exit Preview
            </button>
          )}
        </div>
      )}

      {/* Google Maps-inspired Floating Filter Chip Strip */}
      <div className="cercos-map-filters">
        <button
          type="button"
          className={`cercos-chip ${filterMode === 'all' ? 'active' : ''}`}
          onClick={() => setFilterMode('all')}
        >
          All Stations ({stations.length})
        </button>
        {recommendation && (
          <button
            type="button"
            className={`cercos-chip ${filterMode === 'recommended' ? 'active' : ''}`}
            onClick={() => setFilterMode('recommended')}
          >
            ★ Top 3 Recommended
          </button>
        )}
        <button
          type="button"
          className={`cercos-chip ${filterMode === 'fast' ? 'active' : ''}`}
          onClick={() => setFilterMode('fast')}
        >
          ⚡ Fast ≥50kW
        </button>
        <button
          type="button"
          className={`cercos-chip ${filterMode === 'light_ev' ? 'active' : ''}`}
          onClick={() => setFilterMode('light_ev')}
        >
          🛵 2W / 3W Compatible
        </button>
        <button
          type="button"
          className="cercos-chip fit-btn"
          onClick={() => setFitTrigger((c) => c + 1)}
        >
          ⌖ Fit Route
        </button>
        {onToggleSim && (
          <button
            type="button"
            className={`cercos-chip sim-btn ${simActive ? 'active' : ''}`}
            onClick={onToggleSim}
          >
            {simActive ? '⏹ Stop Preview' : '▶ Preview Drive'}
          </button>
        )}
      </div>

      {/* Bottom-Right Map Control Stack (Google Maps FAB style) */}
      <div className="gmaps-fab-stack">
        {onOpenLanding && (
          <button
            type="button"
            className="gmaps-fab"
            onClick={onOpenLanding}
            title="Show CERCOS Overview Landing"
          >
            ✨ Overview
          </button>
        )}
        <button
          type="button"
          className="gmaps-fab"
          onClick={() => setLegendExpanded((v) => !v)}
          title="Toggle Map Legend"
        >
          {legendExpanded ? 'Hide Key' : 'Map Key'}
        </button>
      </div>

      {/* Collapsible Map Key / Legend */}
      <div className={`cercos-map-legend ${legendExpanded ? 'expanded' : 'compact'}`}>
        <div className="legend-title">EV Station Highlights</div>
        {legendExpanded ? (
          <>
            <div className="legend-row">
              <span className="dot" style={{ background: '#059669', border: '2px solid #facc15' }} />
              <span>★ #1 CERCOS Optimal Stop</span>
            </div>
            <div className="legend-row">
              <span className="dot" style={{ background: '#0d9488' }} />
              <span>#2 &amp; #3 Ranked Alternatives</span>
            </div>
            <div className="legend-row">
              <span className="dot" style={{ background: '#d97706' }} />
              <span>NR — Naïve Nearest Station</span>
            </div>
            <div className="legend-row">
              <span className="dot" style={{ background: '#6366f1' }} />
              <span>DC Fast Hub (≥ 50 kW)</span>
            </div>
            <div className="legend-row">
              <span className="dot" style={{ background: '#0284c7' }} />
              <span>AC / 2W-3W Station (&lt; 50 kW)</span>
            </div>
            <div className="legend-row">
              <span className="dot" style={{ background: '#dc2626' }} />
              <span>✕ Filtered (Plug / SoC Reserve)</span>
            </div>
            <div className="legend-row">
              <span className="dot" style={{ background: '#1a73e8' }} />
              <span>Real Road Route (OSRM)</span>
            </div>
          </>
        ) : (
          <div className="legend-compact-pills">
            <span>🟢 #1 Stop</span>
            <span>🔵 Highway Leg</span>
            <span>⚡ ≥50kW</span>
            <span>✕ Filtered</span>
          </div>
        )}
      </div>

      <MapContainer
        center={center}
        zoom={zoom}
        style={{ width: '100%', height: '100%' }}
        scrollWheelZoom={true}
      >
        <MapViewportController
          stations={stations}
          selectedStation={selectedStation}
          focusedStepLoc={focusedStepLoc}
          simPosition={simPosition}
          origin={origin}
          destination={destination}
          fitTrigger={fitTrigger}
        />

        {!isJsdom && (
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
        )}

        {/* Leg 1: Google Maps Layered Highway Polyline (Dark Azure Casing + Bright Nav Blue) */}
        {!isJsdom && leg1Coords.length >= 2 && (
          <>
            <Polyline
              positions={leg1Coords}
              pathOptions={{ color: '#0b4a9f', weight: 9, opacity: 0.72, lineCap: 'round' }}
            />
            <Polyline
              positions={leg1Coords}
              pathOptions={{ color: '#1a73e8', weight: 5, opacity: 0.96, lineCap: 'round' }}
            />
          </>
        )}

        {/* Leg 2: Post-Charge Continuation Highway Polyline */}
        {!isJsdom && leg2Coords.length >= 2 && (
          <>
            <Polyline
              positions={leg2Coords}
              pathOptions={{ color: '#065f46', weight: 8, opacity: 0.45, dashArray: '12 9' }}
            />
            <Polyline
              positions={leg2Coords}
              pathOptions={{
                color: '#10b981',
                weight: 4.5,
                opacity: 0.95,
                dashArray: '10 8',
                className: 'cercos-marching-route',
              }}
            />
          </>
        )}

        {/* Animated Navigation EV Cursor */}
        {simActive && simPosition && <Marker position={simPosition} icon={navPuckIcon()} />}

        {origin && (
          <Marker position={[origin.lat, origin.lon]} icon={endpointIcon('START', '#0f172a')} />
        )}
        {destination && (
          <Marker
            position={[destination.lat, destination.lon]}
            icon={endpointIcon('DEST', '#1a73e8')}
          />
        )}

        {filteredStations.map((station) => {
          const [lon, lat] = station.geometry.coordinates
          const p = station.properties
          const id = p.station_id
          const name = p.name || p.station_name || `Station #${id}`
          const kw = p.max_power_kw ?? 22
          const rank = rankByStationId.get(id)
          const rejectReason = rejectedReasons.get(id)
          const isNearest = nearestBaseline?.station_id === id
          const isSelected = selectedStationId === id

          let bg = kw >= 50 ? '#6366f1' : '#0284c7'
          let border = '#ffffff'
          let label = kw >= 50 ? `⚡${Math.round(kw)}` : `${Math.round(kw)}`
          let size = 28
          let pulse = false

          if (rejectReason || p.is_operational === false) {
            bg = '#dc2626'
            label = '✕'
            size = 22
          } else if (rank === 1) {
            bg = '#059669'
            border = '#facc15'
            label = '★#1'
            size = 38
            pulse = true
          } else if (rank === 2 || rank === 3) {
            bg = '#0d9488'
            border = '#a7f3d0'
            label = `#${rank}`
            size = 34
          } else if (isNearest && recommendation) {
            bg = '#d97706'
            border = '#fef08a'
            label = 'NR'
            size = 30
          }

          return (
            <Marker
              key={id}
              position={[lat, lon]}
              icon={createPinIcon({ bg, border, label, size, pulse, selected: isSelected })}
              eventHandlers={{
                click: () => onSelectStation?.(station),
              }}
            >
              {(rank === 1 || isNearest) && (
                <Tooltip permanent direction="top" offset={[0, -18]} className="cercos-pin-tooltip">
                  {rank === 1
                    ? `★ #1 ${p.cpo_name ?? ''} (${kw} kW)`
                    : `Nearest: ${p.cpo_name ?? ''}`}
                </Tooltip>
              )}
              <Popup>
                <div className="cercos-popup">
                  <div className="popup-badges">
                    {rank && <span className="badge-rank">CERCOS Rank #{rank}</span>}
                    {isNearest && <span className="badge-nearest">Nearest Stop</span>}
                    <span className="badge-source">{(p.source || 'ocm').toUpperCase()}</span>
                  </div>
                  <h4>{name}</h4>
                  <div className="popup-meta">
                    <div>
                      <strong>CPO:</strong> {p.cpo_name || 'Public'}
                    </div>
                    <div>
                      <strong>Power:</strong> {kw} kW · <strong>Tariff:</strong>{' '}
                      {formatTariff(p.tariff_inr_kwh)}
                    </div>
                    <div>
                      <strong>Connectors:</strong> {(p.connector_types || ['Type2']).join(', ')}
                    </div>
                    <div>
                      <strong>Hours:</strong> {p.hours_text || '24/7'} ·{' '}
                      <strong>Confidence:</strong> {Math.round((p.confidence ?? 0.85) * 100)}%
                    </div>
                    {p.address && <div className="popup-addr">{p.address}</div>}
                    {rejectReason && (
                      <div className="popup-reject">
                        <strong>Rejected:</strong> {rejectReason}
                      </div>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}
