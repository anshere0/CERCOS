import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'
import { MapView } from './components/MapView'
import type { StationFeature } from './api/client'

describe('CERCOS Frontend Smoke Tests', () => {
  it('renders application header and branding', () => {
    render(<App />)
    expect(screen.getByText('CERCOS')).toBeInTheDocument()
    expect(
      screen.getByText('Cognitive EV Route & Charging Optimization'),
    ).toBeInTheDocument()
  })

  it('finds the dedicated map container in the DOM', () => {
    render(<App />)
    const mapWrapper = screen.getByTestId('map-container')
    expect(mapWrapper).toBeInTheDocument()
    expect(mapWrapper.querySelector('.leaflet-container')).toBeInTheDocument()
  })

  it('renders EV charging station filter pills and markers when stations passed', () => {
    const sample: StationFeature[] = [
      {
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [77.4299, 23.2326] },
        properties: {
          station_id: 1,
          station_name: 'DB City Mall EV Hub',
          cpo_name: 'Tata Power',
          max_power_kw: 60,
          tariff_inr_kwh: 19,
          source: 'osm',
          confidence: 0.94,
          connector_types: ['CCS2'],
        },
      },
    ]
    render(<MapView stations={sample} />)
    expect(screen.getByText('All Stations (1)')).toBeInTheDocument()
    expect(screen.getByText('EV Station Highlights')).toBeInTheDocument()
  })
})
