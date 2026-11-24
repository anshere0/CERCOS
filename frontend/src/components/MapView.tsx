import React from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const BHOPAL_CENTER: [number, number] = [23.2599, 77.4126]
const DEFAULT_ZOOM = 11

const markerIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

export interface MapViewProps {
  center?: [number, number]
  zoom?: number
}

export const MapView: React.FC<MapViewProps> = ({
  center = BHOPAL_CENTER,
  zoom = DEFAULT_ZOOM,
}) => {
  return (
    <div
      data-testid="map-container"
      className="cercos-map-wrapper"
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        minHeight: '300px',
      }}
    >
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
        <Marker position={center} icon={markerIcon}>
          <Popup>
            <div style={{ padding: '4px' }}>
              <h4 style={{ margin: '0 0 4px', fontSize: '14px', fontWeight: 600 }}>
                Bhopal Central Hub
              </h4>
              <p style={{ margin: 0, fontSize: '12px', color: '#4b5563' }}>
                CERCOS Regional EV Charging Corridor Reference Point
              </p>
            </div>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  )
}
