import { http, HttpResponse } from 'msw'
import type { RecommendResult, StationFeatureCollection, VehicleProfile } from '../api/client'

export const mockStations: StationFeatureCollection = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [77.4345, 23.2332] }, // MP Nagar Bhopal
      properties: {
        station_id: 101,
        name: 'MP Nagar Zone-II Fast EV Station',
        cpo_name: 'Tata Power EZ Charge',
        max_power_kw: 60,
        tariff_inr_kwh: 15.5,
        rating: 4.7,
        is_operational: true,
        connector_types: ['CCS2', 'Type-2'],
        source: 'synthetic',
        confidence: 0.95,
      },
    },
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [77.4012, 23.2599] }, // Bhopal Junction / Old City
      properties: {
        station_id: 102,
        name: 'Bhopal Railway Stn West EV Point',
        cpo_name: 'Bhopal Smart City Ltd',
        max_power_kw: 30,
        tariff_inr_kwh: 13.0,
        rating: 4.2,
        is_operational: true,
        connector_types: ['CCS2', 'Bharat DC-001', 'Type-2'],
        source: 'osm',
        confidence: 0.88,
      },
    },
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [77.3621, 23.2185] }, // Kolar Road
      properties: {
        station_id: 103,
        name: 'Kolar Road Green Corridor Charger',
        cpo_name: 'Jio-bp pulse',
        max_power_kw: 50,
        tariff_inr_kwh: 16.0,
        rating: 4.5,
        is_operational: true,
        connector_types: ['CCS2'],
        source: 'census',
        confidence: 0.92,
      },
    },
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [77.0851, 23.2031] }, // Sehore Corridor (SH-18 / NH-46)
      properties: {
        station_id: 104,
        name: 'Sehore Highway Food Plaza EV Stop',
        cpo_name: 'Statiq',
        max_power_kw: 60,
        tariff_inr_kwh: 17.5,
        rating: 4.4,
        is_operational: true,
        connector_types: ['CCS2', 'Type-2'],
        source: 'synthetic',
        confidence: 0.9,
      },
    },
  ],
}

export const mockVehicles: VehicleProfile[] = [
  {
    id: 1,
    segment: 'E2W',
    make_model: 'Ola S1 Pro (Gen 2)',
    battery_kwh: 4.0,
    wh_per_km: 28,
    max_dc_kw: 1.5,
    max_ac_kw: 0.75,
    connector_types: ['Type-2', 'Proprietary-AC'],
  },
  {
    id: 2,
    segment: 'E3W',
    make_model: 'Mahindra Treo Zor',
    battery_kwh: 7.37,
    wh_per_km: 65,
    max_dc_kw: 3.3,
    max_ac_kw: 3.3,
    connector_types: ['IEC-60309', 'Type-2'],
  },
  {
    id: 3,
    segment: 'E4W',
    make_model: 'Tata Nexon EV LR',
    battery_kwh: 40.5,
    wh_per_km: 135,
    max_dc_kw: 50.0,
    max_ac_kw: 7.2,
    connector_types: ['CCS2', 'Type-2'],
  },
]

export const mockRecommendResult: RecommendResult = {
  needs_charging: true,
  reachable_km: 42.5,
  top3: [
    {
      station_id: 101,
      name: 'MP Nagar Zone-II Fast EV Station',
      score: 0.892,
      rank: 1,
      eta_extra_min: 12.0,
      est_cost_inr: 155.0,
      est_charge_min: 22.0,
      arrival_soc_pct: 18.5,
      criteria: {
        detour_km: 1.5,
        cost_inr_kwh: 15.5,
        wait_min: 4.0,
        effective_kw: 30.0,
        rating: 4.7,
        arrival_soc_pct: 18.5,
      },
      explain: [
        {
          criterion: 'wait_min',
          contribution: 0.35,
          note: 'Short queue wait time observed (4 min)',
        },
        {
          criterion: 'effective_kw',
          contribution: 0.3,
          note: 'Accepts maximum charging capacity of vehicle (30 kW)',
        },
        {
          criterion: 'detour_km',
          contribution: 0.2,
          note: 'Minimal detour (1.5 km off corridor)',
        },
      ],
      source: 'synthetic',
      confidence: 0.95,
    },
    {
      station_id: 103,
      name: 'Kolar Road Green Corridor Charger',
      score: 0.814,
      rank: 2,
      eta_extra_min: 19.0,
      est_cost_inr: 160.0,
      est_charge_min: 25.0,
      arrival_soc_pct: 15.0,
      criteria: {
        detour_km: 3.2,
        cost_inr_kwh: 16.0,
        wait_min: 8.0,
        effective_kw: 30.0,
        rating: 4.5,
        arrival_soc_pct: 15.0,
      },
      explain: [
        {
          criterion: 'rating',
          contribution: 0.28,
          note: 'High reliability rating (4.5/5)',
        },
        {
          criterion: 'cost_inr_kwh',
          contribution: 0.25,
          note: 'Competitive commercial tariff',
        },
      ],
      source: 'census',
      confidence: 0.92,
    },
    {
      station_id: 102,
      name: 'Bhopal Railway Stn West EV Point',
      score: 0.768,
      rank: 3,
      eta_extra_min: 24.0,
      est_cost_inr: 130.0,
      est_charge_min: 30.0,
      arrival_soc_pct: 12.2,
      criteria: {
        detour_km: 4.1,
        cost_inr_kwh: 13.0,
        wait_min: 15.0,
        effective_kw: 25.0,
        rating: 4.2,
        arrival_soc_pct: 12.2,
      },
      explain: [
        {
          criterion: 'cost_inr_kwh',
          contribution: 0.42,
          note: 'Cheapest tariff (₹13.00/kWh municipal rate)',
        },
        {
          criterion: 'wait_min',
          contribution: -0.18,
          note: 'Longer estimated queue (15 min)',
        },
      ],
      source: 'osm',
      confidence: 0.88,
    },
  ],
  rejected: [
    {
      station_id: 999,
      reason: 'Connector type incompatible with requested vehicle profile',
    },
  ],
  warnings: [
    'Synthetic demonstration data: live backend mock active',
    'Haversine corridor distance approximation factor x1.3 applied',
  ],
  engine_version: 'v0.1.0-draft-contract',
}

export const handlers = [
  http.get('*/v1/modes', () => {
    return HttpResponse.json({
      modes: ['Cheapest', 'Fastest', 'Shortest', 'HighestRated', 'BatterySafe', 'Balanced'],
      default_weights: {
        Cheapest: [0.1, 0.45, 0.15, 0.1, 0.1, 0.1],
        Fastest: [0.15, 0.1, 0.35, 0.3, 0.05, 0.05],
        Balanced: [0.2, 0.2, 0.2, 0.15, 0.15, 0.1],
      },
    })
  }),

  http.get('*/v1/vehicles', () => {
    return HttpResponse.json(mockVehicles)
  }),

  http.get('*/v1/stations', () => {
    return HttpResponse.json(mockStations)
  }),

  http.get('*/v1/stations/:id', ({ params }) => {
    const id = Number(params.id)
    const match = mockStations.features.find((f) => f.properties.station_id === id)
    if (match) return HttpResponse.json(match)
    return new HttpResponse('Station not found', { status: 404 })
  }),

  http.post('*/v1/recommend', () => {
    return HttpResponse.json(mockRecommendResult)
  }),

  http.post('*/v1/field/census', () => {
    return HttpResponse.json({ status: 'created', id: 101 }, { status: 201 })
  }),

  http.post('*/v1/field/survey', () => {
    return HttpResponse.json({ status: 'created', id: 201 }, { status: 201 })
  }),

  http.post('*/v1/field/queue', () => {
    return HttpResponse.json({ status: 'created', id: 301 }, { status: 201 })
  }),

  http.get('*/v1/field/export/:kind', ({ params }) => {
    const kind = params.kind
    const csvSample = `kind,station_name,lat,lon,timestamp\n${kind},Sample Station,23.2599,77.4126,2026-11-21T10:00:00Z`
    return new HttpResponse(csvSample, {
      headers: { 'Content-Type': 'text/csv' },
    })
  }),
]
