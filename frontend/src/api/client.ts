import { components } from './types'

export type LatLon = components['schemas']['LatLon']
export type RecommendRequest = components['schemas']['RecommendRequest']

export interface RecommendCriterionExplanation {
  criterion: string
  contribution: number
  note: string
}

export interface RecommendedStation {
  station_id: number
  name: string
  score: number
  rank: number
  eta_extra_min: number
  est_cost_inr: number
  est_charge_min: number
  arrival_soc_pct: number
  criteria: {
    detour_km: number
    cost_inr_kwh: number
    wait_min: number
    effective_kw: number
    rating: number
    arrival_soc_pct: number
  }
  explain: RecommendCriterionExplanation[]
  source: 'synthetic' | 'osm' | 'census' | 'openchargemap'
  confidence: number
}

export interface RejectedStation {
  station_id: number
  reason: string
}

export interface RecommendResult {
  needs_charging: boolean
  reachable_km: number
  top3: RecommendedStation[]
  rejected: RejectedStation[]
  warnings: string[]
  engine_version: string
}

export interface VehicleProfile {
  id: number
  segment: 'E2W' | 'E3W' | 'E4W' | 'ELCV'
  make_model: string
  battery_kwh: number
  wh_per_km: number
  max_dc_kw: number
  max_ac_kw: number
  connector_types: string[]
}

export interface StationFeature {
  type: 'Feature'
  geometry: {
    type: 'Point'
    coordinates: [number, number] // [lon, lat]
  }
  properties: {
    station_id: number
    name: string
    cpo_name: string
    max_power_kw: number
    tariff_inr_kwh: number
    rating: number
    is_operational: boolean
    connector_types: string[]
    source: string
    confidence: number
  }
}

export interface StationFeatureCollection {
  type: 'FeatureCollection'
  features: StationFeature[]
}

export interface CensusPayload {
  station_name: string
  operator: string
  lat: number
  lon: number
  address: string
  n_connectors: number
  connector_types: string[]
  max_kw: number
  tariff_inr_kwh?: number
  hours_24x7: boolean
  payment_methods?: string[]
  app_required?: boolean
  working_yn: boolean
  notes?: string
  enumerator: string
}

export interface SurveyPayload {
  consent: boolean
  segment: 'E2W' | 'E3W' | 'E4W' | 'fleet'
  model?: string
  battery_kwh_if_known?: number
  home_charge_yn: boolean
  trips_per_week_beyond_30km?: number
  range_anxiety_1_5?: number
  best_criterion: string
  worst_criterion: string
  ratings: Record<string, number>
  willingness_to_pay_extra_per_kwh_for_zero_wait?: number
}

export interface QueuePayload {
  station_id: number
  date: string
  slot: '07-10' | '12-15' | '18-21'
  minute_stamp: string
  vehicles_waiting: number
  connectors_busy: number
  session_start?: string
  session_end?: string
  observer: string
}

const getBaseUrl = (): string => {
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${getBaseUrl()}${endpoint}`
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`API error ${response.status} from ${endpoint}: ${errorText}`)
  }

  return response.json() as Promise<T>
}

export const cercosApi = {
  // Mode & configuration
  getModes: () => request<{ modes: string[]; default_weights: Record<string, number[]> }>('/v1/modes'),

  // Vehicles
  getVehicles: () => request<VehicleProfile[]>('/v1/vehicles'),

  // Stations
  getStations: (bbox: string, source?: string) => {
    const params = new URLSearchParams({ bbox })
    if (source) params.append('source', source)
    return request<StationFeatureCollection>(`/v1/stations?${params.toString()}`)
  },

  getStationDetail: (id: number) => request<StationFeature>(`/v1/stations/${id}`),

  // Recommendation engine
  recommend: (body: RecommendRequest) =>
    request<RecommendResult>('/v1/recommend', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  // Field Mode instruments
  submitCensus: (payload: CensusPayload) =>
    request<{ status: 'created'; id: number }>('/v1/field/census', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  submitSurvey: (payload: SurveyPayload) =>
    request<{ status: 'created'; id: number }>('/v1/field/survey', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  submitQueue: (payload: QueuePayload) =>
    request<{ status: 'created'; id: number }>('/v1/field/queue', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  exportFieldData: async (kind: 'census' | 'survey' | 'queue'): Promise<string> => {
    const url = `${getBaseUrl()}/v1/field/export/${kind}`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`Failed to export ${kind} data: ${response.statusText}`)
    }
    return response.text()
  },
}
