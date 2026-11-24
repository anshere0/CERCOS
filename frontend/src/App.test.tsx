import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from './App'

describe('CERCOS Frontend Smoke Tests', () => {
  it('renders application header and branding', () => {
    render(<App />)
    expect(screen.getByText('CERCOS')).toBeInTheDocument()
    expect(
      screen.getByText('Cognitive EV Route & Charging Optimization'),
    ).toBeInTheDocument()
  })

  it('renders Mock data banner when mock mode is active', () => {
    render(<App />)
    expect(screen.getByText('Mock data')).toBeInTheDocument()
  })

  it('finds the map container in the DOM', () => {
    render(<App />)
    const mapWrapper = screen.getByTestId('map-container')
    expect(mapWrapper).toBeInTheDocument()
    expect(mapWrapper.querySelector('.leaflet-container')).toBeInTheDocument()
  })
})
