import React from 'react'
import { MapView } from './components/MapView'
import { MockBanner } from './components/MockBanner'
import './App.css'

export const App: React.FC = () => {
  const useMocks = import.meta.env.VITE_USE_MOCKS !== 'false'

  return (
    <div className="cercos-app">
      <MockBanner visible={useMocks} />
      <header className="cercos-header">
        <div className="cercos-brand">
          <h1 className="cercos-title">CERCOS</h1>
          <span className="cercos-subtitle">
            Cognitive EV Route & Charging Optimization
          </span>
        </div>
        <div className="cercos-header-meta">
          <span className="cercos-badge">Bhopal Region (≤100km)</span>
          <span className="cercos-badge">P4 Frontend MVP</span>
        </div>
      </header>
      <main className="cercos-main">
        <div className="cercos-control-card">
          <h3>Bhopal EV Corridor Map</h3>
          <p>
            Centered at 23.26°N, 77.41°E (Zoom 11). Ready for corridor routing,
            station overlays, and field mode census instruments.
          </p>
        </div>
        <MapView />
      </main>
    </div>
  )
}

export default App
