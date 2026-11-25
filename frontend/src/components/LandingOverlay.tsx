import React, { useEffect, useRef, useState } from 'react'
import gsap from 'gsap'
import { useGSAP } from '@gsap/react'
import type { SystemStatusResponse } from '../api/client'

gsap.registerPlugin()

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

const STATS = [
  { value: '508', label: 'Verified Stations', suffix: '' },
  { value: '97.2', label: 'Fleet Coverage', suffix: '%' },
  { value: '0.0', label: 'Rank Reversal', suffix: '%' },
  { value: '8.0', label: 'SoC Safety Buffer', suffix: '%' },
]

export const LandingOverlay: React.FC<LandingOverlayProps> = ({
  visible,
  stationCount,
  statusInfo,
  presets,
  onLaunchNavigator,
  onSelectCorridor,
  onOpenAudit,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [counters, setCounters] = useState<number[]>([0, 0, 0, 0])

  // Animated counter effect
  useEffect(() => {
    if (!visible) return
    const targets = [statusInfo?.stations_total || stationCount || 508, 97.2, 0.0, 8.0]
    const duration = 1800
    const start = Date.now()
    let rafId = 0
    const frame = () => {
      const elapsed = Date.now() - start
      const progress = Math.min(elapsed / duration, 1)
      const ease = 1 - Math.pow(1 - progress, 3)
      setCounters(targets.map((t) => +(t * ease).toFixed(1)))
      if (progress < 1) {
        rafId = requestAnimationFrame(frame)
      }
    }
    rafId = requestAnimationFrame(frame)
    return () => cancelAnimationFrame(rafId)
  }, [visible, stationCount, statusInfo])

  useGSAP(
    () => {
      if (!visible || !containerRef.current) return

      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })

      tl.fromTo(
        '.landing-glow-orb',
        { scale: 0, opacity: 0 },
        { scale: 1, opacity: 1, duration: 1.2 },
      )
        .fromTo(
          '.landing-kicker-anim',
          { y: 20, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6 },
          '-=0.6',
        )
        .fromTo(
          '.landing-h2-line',
          { y: 40, opacity: 0, clipPath: 'inset(100% 0 0 0)' },
          { y: 0, opacity: 1, clipPath: 'inset(0% 0 0 0)', duration: 0.7, stagger: 0.12 },
          '-=0.3',
        )
        .fromTo(
          '.landing-copy-anim',
          { y: 15, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.5 },
          '-=0.3',
        )
        .fromTo(
          '.landing-cta-anim',
          { y: 20, opacity: 0, scale: 0.95 },
          { y: 0, opacity: 1, scale: 1, duration: 0.5, stagger: 0.1 },
          '-=0.2',
        )
        .fromTo(
          '.kpi-card-anim',
          { y: 30, opacity: 0, scale: 0.9 },
          { y: 0, opacity: 1, scale: 1, duration: 0.45, stagger: 0.08 },
          '-=0.25',
        )
        .fromTo(
          '.showcase-panel-anim',
          { x: 40, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.6, stagger: 0.15 },
          '-=0.5',
        )
    },
    { scope: containerRef, dependencies: [visible] },
  )

  if (!visible) return null

  const totalStations = statusInfo?.stations_total || stationCount || 508

  return (
    <section
      className="landing-backdrop"
      aria-label="CERCOS Overview Landing Showcase"
      data-testid="landing-overlay"
      ref={containerRef}
    >
      {/* Ambient glow orbs */}
      <div className="landing-glow-orb orb-1" />
      <div className="landing-glow-orb orb-2" />
      <div className="landing-glow-orb orb-3" />

      <div className="landing-shell">
        <div className="landing-hero-col">
          <div className="landing-kicker-anim landing-kicker">
            <span className="pulse-dot" />
            <span className="kicker-text">MADHYA PRADESH EV CORRIDOR</span>
            <span className="kicker-badge">LIVE</span>
          </div>

          <h2 className="landing-headline">
            <span className="landing-h2-line">
              Smart EV Routing for
            </span>
            <span className="landing-h2-line headline-gradient">
              Real Indian Roads.
            </span>
          </h2>

          <p className="landing-copy-anim landing-copy">
            Consumer map apps route drivers to the nearest pin—trapping 2W/3W commuters on
            costly DC chargers they cannot absorb. CERCOS pairs live MP charging registries
            with range-reserve math, queue modeling, and turn-by-turn street routing.
          </p>

          <div className="landing-cta-row">
            <button
              type="button"
              className="landing-cta-anim landing-primary-btn"
              onClick={onLaunchNavigator}
            >
              <span className="btn-icon">⚡</span>
              <span>Launch Navigator</span>
              <span className="btn-arrow-wrap">
                <span className="btn-arrow">→</span>
              </span>
            </button>
            <button
              type="button"
              className="landing-cta-anim landing-secondary-btn"
              onClick={onOpenAudit}
            >
              Inspect {totalStations} Stations
            </button>
          </div>

          <div className="landing-kpi-strip">
            {STATS.map((stat, i) => (
              <div key={stat.label} className="kpi-card-anim kpi-card">
                <div className="kpi-value">
                  <span className="kpi-number mono">
                    {i === 0 ? Math.round(counters[i]) : counters[i].toFixed(1)}
                  </span>
                  <span className="kpi-suffix">{stat.suffix}</span>
                </div>
                <span className="kpi-label">{stat.label}</span>
                <div className="kpi-bar">
                  <div
                    className="kpi-bar-fill"
                    style={{
                      width: `${i === 0 ? Math.min(100, (counters[i] / 508) * 100) : counters[i]}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="landing-showcase-col">
          <div className="showcase-panel-anim showcase-card showcase-compare">
            <div className="showcase-card-head">
              <span className="tag-blue">WHY CERCOS</span>
              <span className="tag-pulse" />
            </div>
            <div className="showcase-vs-grid">
              <div className="vs-box vs-bad">
                <div className="vs-icon">📍</div>
                <small>NEAREST-PIN APPS</small>
                <strong>Sends E2W to Highway CCS2</strong>
                <span>₹22/kWh · 32 min queue · Plug mismatch</span>
              </div>
              <div className="vs-box vs-good">
                <div className="vs-icon">⚡</div>
                <small>CERCOS ENGINE</small>
                <strong>Physics-Aware Optimal Stop</strong>
                <span>Verified plug · OSRM routing · &lt;6 min wait</span>
              </div>
            </div>
          </div>

          <div className="showcase-panel-anim showcase-card">
            <div className="showcase-card-head">
              <span className="tag-green">CORRIDORS</span>
              <span>Quick Launch</span>
            </div>
            <div className="quick-routes-list">
              {presets.slice(0, 4).map((p, idx) => (
                <button
                  key={p.id}
                  type="button"
                  className="quick-route-item"
                  onClick={() => onSelectCorridor(p.id)}
                  style={{ animationDelay: `${0.6 + idx * 0.08}s` }}
                >
                  <div className="route-item-info">
                    <strong>{p.label}</strong>
                    <span className="mono route-km">{p.routeKm} km</span>
                  </div>
                  <span className="go-chip">
                    Navigate <span className="go-arrow">→</span>
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
