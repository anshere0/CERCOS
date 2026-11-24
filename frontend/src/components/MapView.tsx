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
import type {
  LatLon,
  NearestBaselineComparison,
  RecommendResult,
  StationFeature,
} from '../api/client'

const BHOPAL_CENTER: [number, number] = [23.2599, 77.4126]
const DEFAULT_ZOOM = 11

type MapFilterMode = 'all' | 'recommended' | 'fast' | 'light_ev'

export interface MapViewProps {
  center?: [number, number]
  zoom?: number
  stations?: StationFeature[]
  recommendation?: RecommendResult | null
  origin?: LatLon | null
  destination?: LatLon | null
  selectedStationId?: number | null
  onSelectStation?: (station: StationFeature) => void
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
    ? 'box-shadow: 0 0 0 4px rgba(255,255,255,0.95), 0 0 16px rgba(16,185,129,0.9);'
    : 'box-shadow: 0 3px 8px rgba(0,0,0,0.35);'
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
      font-size:${size > 32 ? '12px' : '10px'};
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
      padding:3px 8px;
      border-radius:6px;
      background:${bg};
      color:#fff;
      font-weight:700;
      font-size:11px;
      border:2px solid #fff;
      box-shadow:0 3px 8px rgba(0,0,0,0.4);
      white-space:nowrap;
    ">${label}</div>`,
    iconSize: [74, 24],
    iconAnchor: [37, 12],
  })

const MapViewportController: React.FC<{
  stations: StationFeature[]
  selectedStation?: StationFeature | null
  origin?: LatLon | null
  destination?: LatLon | null
  fitTrigger: number
}> = ({ stations, selectedStation, origin, destination, fitTrigger }) => {
  const map = useMap()

  useEffect(() => {
    if (!selectedStation) return
    const [lon, lat] = selectedStation.geometry.coordinates
    try {
      map.flyTo([lat, lon], Math.max(map.getZoom(), 12), { duration: 0.7 })
    } catch {
      // Ignore in test jsdom environment without layout dimensions
    }
  }, [map, selectedStation])

  useEffect(() => {
    const pts: [number, number][] = []
    if (origin) pts.push([origin.lat, origin.lon])
    if (destination) pts.push([destination.lat, destination.lon])
    if (pts.length === 0) {
      stations.forEach((s) => pts.push([s.geometry.coordinates[1], s.geometry.coordinates[0]]))
    }
    if (pts.length >= 2) {
      try {
        map.fitBounds(L.latLngBounds(pts), { padding: [45, 45], maxZoom: 12 })
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
  origin = null,
  destination = null,
  selectedStationId = null,
  onSelectStation,
}) => {
  const [filterMode, setFilterMode] = useState<MapFilterMode>('all')
  const [fitTrigger, setFitTrigger] = useState(0)

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
  const activeRouteCoords: [number, number][] = useMemo(() => {
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

  return (
    <div
      data-testid="map-container"
      className="cercos-map-wrapper"
      style={{ width: '100%', height: '100%', position: 'relative', minHeight: '340px' }}
    >
      {/* Dedicated Map Overlay Filter Bar */}
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
            Top 3 Recommended
          </button>
        )}
        <button
          type="button"
          className={`cercos-chip ${filterMode === 'fast' ? 'active' : ''}`}
          onClick={() => setFilterMode('fast')}
        >
          DC Fast (≥50 kW)
        </button>
        <button
          type="button"
          className={`cercos-chip ${filterMode === 'light_ev' ? 'active' : ''}`}
          onClick={() => setFilterMode('light_ev')}
        >
          E2W / E3W Compatible
        </button>
        <button
          type="button"
          className="cercos-chip fit-btn"
          onClick={() => setFitTrigger((c) => c + 1)}
          title="Zoom to entire corridor"
        >
          Fit Corridor
        </button>
      </div>

      {/* Dedicated Map Legend */}
      <div className="cercos-map-legend">
        <div className="legend-title">EV Station Highlights</div>
        <div className="legend-row">
          <span className="dot" style={{ background: '#059669', border: '2px solid #facc15' }} />
          <span>★ #1 Best CERCOS Pick</span>
        </div>
        <div className="legend-row">
          <span className="dot" style={{ background: '#0d9488' }} />
          <span>#2 / #3 Alternative Picks</span>
        </div>
        <div className="legend-row">
          <span className="dot" style={{ background: '#6366f1' }} />
          <span>DC Fast Charger (≥50 kW)</span>
        </div>
        <div className="legend-row">
          <span className="dot" style={{ background: '#0284c7' }} />
          <span>AC / 2W-3W Community Charger</span>
        </div>
        <div className="legend-row">
          <span className="dot" style={{ background: '#dc2626' }} />
          <span>Filtered / Out of Range</span>
        </div>
      </div>

      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        style={{ width: '100%', height: '100%', zIndex: 1 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapViewportController
          stations={stations}
          selectedStation={selectedStation}
          origin={origin}
          destination={destination}
          fitTrigger={fitTrigger}
        />

        {/* Highlighted Recommended Route Line */}
        {!isJsdom && origin && destination && (
          <Polyline
            positions={[
              [origin.lat, origin.lon],
              [destination.lat, destination.lon],
            ]}
            pathOptions={{ color: '#64748b', weight: 2, dashArray: '6 8', opacity: 0.65 }}
          />
        )}

        {!isJsdom && activeRouteCoords.length >= 2 && (
          <Polyline
            positions={activeRouteCoords}
            pathOptions={{ color: '#10b981', weight: 4.5, opacity: 0.9 }}
          />
        )}

        {/* Origin & Destination Markers */}
        {origin && (
          <Marker position={[origin.lat, origin.lon]} icon={endpointIcon('ORIGIN', '#16a34a')}>
            <Popup>
              <strong>Route Origin</strong>
              <div>
                {origin.lat.toFixed(4)}°N, {origin.lon.toFixed(4)}°E
              </div>
            </Popup>
          </Marker>
        )}

        {destination && (
          <Marker
            position={[destination.lat, destination.lon]}
            icon={endpointIcon('DEST', '#1e293b')}
          >
            <Popup>
              <strong>Route Destination</strong>
              <div>
                {destination.lat.toFixed(4)}°N, {destination.lon.toFixed(4)}°E
              </div>
            </Popup>
          </Marker>
        )}

        {/* Dynamic EV Charging Station Markers */}
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
            size = 24
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
                  {rank === 1 ? `★ #1 ${p.cpo_name ?? ''} (${kw} kW)` : `Nearest: ${p.cpo_name ?? ''}`}
                </Tooltip>
              )}
              <Popup>
                <div className="cercos-popup">
                  <div className="popup-badges">
                    {rank && <span className="badge-rank">CERCOS Rank #{rank}</span>}
                    {isNearest && <span className="badge-nearest">Nearest Stop</span>}
                    <span className="badge-source">{(p.source || 'osm').toUpperCase()}</span>
                  </div>
                  <h4>{name}</h4>
                  <div className="popup-meta">
                    <div>
                      <strong>CPO:</strong> {p.cpo_name || 'Public'}
                    </div>
                    <div>
                      <strong>Power:</strong> {kw} kW · <strong>Tariff:</strong>{' '}
                      {p.tariff_inr_kwh == null
                        ? 'Unlisted (est. ₹18/kWh)'
                        : p.tariff_inr_kwh === 0
                          ? 'Free (₹0/kWh)'
                          : `₹${p.tariff_inr_kwh}/kWh`}
                    </div>
                    <div>
                      <strong>Connectors:</strong>{' '}
                      {(p.connector_types || ['Type2']).join(', ')}
                    </div>
                    <div>
                      <strong>Hours:</strong> {p.hours_text || '24/7'} · <strong>Confidence:</strong>{' '}
                      {Math.round((p.confidence ?? 0.9) * 100)}%
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
