import React from 'react'
import type { SystemStatusResponse } from '../api/client'

export interface CorridorQuickLaunch {
  id: string
  label: string
  routeKm: number
}

export interface LandingOverlayProps {
  visible: boolean
  stationCount: number
  statusInfo: SystemStatusResponse | null
  presets: CorridorQuickLaunch[]
  onLaunchNavigator: () => void
  onSelectCorridor: (presetId: string) => void
  onOpenAudit: () => void
}

export const LandingOverlay: React.FC<LandingOverlayProps> = ({
  visible,
  stationCount,
  statusInfo,
  presets,
  onLaunchNavigator,
  onSelectCorridor,
  onOpenAudit,
}) => {
  if (!visible) return null

  const totalStations = statusInfo?.stations_total || stationCount || 508

  return (
    <section
      className="landing-backdrop"
      aria-label="CERCOS Overview Landing Showcase"
      data-testid="landing-overlay"
    >
      <div className="landing-shell">
        <div className="landing-hero-col">
          <div className="landing-kicker">
            <span className="pulse-dot" />
            MADHYA PRADESH CORRIDOR · NH-46 &amp; URBAN GRID
          </div>

          <h2 className="landing-headline">
            EV Navigation Built for{' '}
            <span className="headline-accent">Real Physics &amp; Indian Roads.</span>
          </h2>

          <p className="landing-copy">
            Consumer map apps simply route drivers to the nearest pin—trapping 2W/3W commuters on
            costly 60 kW DC chargers they cannot absorb (`P_eff` bottleneck) or sending vehicles to
            congested, incompatible plazas. CERCOS pairs live multi-source MP charging registries
            with deterministic range-reserve math, M/G/c queuing, and turn-by-turn street routing.
          </p>

          <div className="landing-cta-row">
            <button type="button" className="landing-primary-btn" onClick={onLaunchNavigator}>
              <span>Launch Live Navigator</span>
              <span className="btn-arrow">→</span>
            </button>
            <button type="button" className="landing-secondary-btn" onClick={onOpenAudit}>
              Inspect {totalStations} Verified Stations
            </button>
          </div>

          <div className="landing-kpi-strip">
            <div className="kpi-pill">
              <strong className="mono">{totalStations}</strong>
              <span>Verified MP Stations</span>
            </div>
            <div className="kpi-pill">
              <strong className="mono">97.2%</strong>
              <span>2W/3W Fleet Coverage</span>
            </div>
            <div className="kpi-pill">
              <strong className="mono">0.0%</strong>
              <span>MCDM Rank Reversal</span>
            </div>
            <div className="kpi-pill">
              <strong className="mono">8.0%</strong>
              <span>Mandatory SoC Buffer</span>
            </div>
          </div>
        </div>

        <div className="landing-showcase-col">
          <div className="showcase-card showcase-compare">
            <div className="showcase-card-head">
              <span className="tag-blue">CORE BREAKTHROUGH</span>
              <span>Proximity Routing vs CERCOS Engine</span>
            </div>
            <div className="showcase-vs-grid">
              <div className="vs-box vs-bad">
                <small>NAÏVE NEAREST APP</small>
                <strong>Routes E2W/E3W to Highway CCS2</strong>
                <span>₹22/kWh commercial tariff · 32 min peak queue · Plug mismatch risk</span>
              </div>
              <div className="vs-box vs-good">
                <small>★ CERCOS RECOMMENDED</small>
                <strong>Bottleneck &amp; Wait-Aware Stop</strong>
                <span>Verified LECCS/CCS2 match · Live OSRM road route · M/G/c wait &lt; 6 min</span>
              </div>
            </div>
          </div>

          <div className="showcase-card">
            <div className="showcase-card-head">
              <span className="tag-green">QUICK ROUTE LAUNCH</span>
              <span>Start Animated Corridor Preview</span>
            </div>
            <div className="quick-routes-list">
              {presets.slice(0, 4).map((p) => (
                <button
                  key={p.id}
                  type="button"
                  className="quick-route-item"
                  onClick={() => onSelectCorridor(p.id)}
                >
                  <div>
                    <strong>{p.label}</strong>
                    <span className="mono">{p.routeKm} km NH-46 / Corridor</span>
                  </div>
                  <span className="go-chip">Navigate →</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
