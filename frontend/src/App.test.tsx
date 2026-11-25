import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'
import { MapView } from './components/MapView'
import type { StationFeature, VehicleProfile } from './api/client'

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

  it('renders landing showcase overlay and launches navigator with live search bar', () => {
    render(<App />)
    expect(screen.getByTestId('landing-overlay')).toBeInTheDocument()
    const launchBtn = screen.getByRole('button', { name: /Launch Navigator/i })
    fireEvent.click(launchBtn)
    expect(screen.queryByTestId('landing-overlay')).not.toBeInTheDocument()
    expect(screen.getByLabelText('Origin location')).toBeInTheDocument()
    expect(screen.getByLabelText('Destination location')).toBeInTheDocument()
    expect(screen.getByLabelText('Use my live location')).toBeInTheDocument()
  })

  it('renders EV charging station filter pills and plain-English compatibility indicators', () => {
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
    const scooter: VehicleProfile = {
      vehicle_id: 1,
      segment: 'E2W',
      model_name: 'Ather 450X',
      battery_kwh: 3.7,
      wh_per_km: 33,
      max_dc_kw: null,
      max_ac_kw: 1.5,
      connector_types: ['LECCS', '15A_Socket'],
    }
    render(<MapView stations={sample} activeVehicle={scooter} />)
    expect(screen.getByText('All (1)')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Compatible/i })).toBeInTheDocument()
    expect(screen.getByText('1 incompatible')).toBeInTheDocument()
  })
})
