import { components } from './types'

export type LatLon = components['schemas']['LatLon']
export type RecommendRequest = components['schemas']['RecommendRequest'] & {
  route_km?: number | null
  vehicle_model?: string | null
}

export interface RecommendCriterionExplanation {
  criterion: string
  contribution: number
  note: string | null
}

export interface RecommendedStation {
  station_id: number
  name: string
  cpo_name?: string | null
  lat?: number | null
  lon?: number | null
  connectors?: string[]
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
  source: string
  confidence: number
}

export interface RejectedStation {
  station_id: number
  reason: string
}

export interface NearestBaselineComparison {
  station_id: number
  name: string
  cpo_name?: string | null
  lat: number
  lon: number
  distance_from_origin_km: number
  detour_km: number
  tariff_inr_kwh: number
  raw_power_kw: number
  effective_kw: number
  wait_min: number
  is_compatible: boolean
  cost_diff_vs_cercos_inr_kwh: number
  wait_diff_vs_cercos_min: number
}

export interface RecommendResult {
  needs_charging: boolean
  reachable_km: number
  route_km?: number | null
  top3: RecommendedStation[]
  rejected: RejectedStation[]
  nearest_baseline?: NearestBaselineComparison | null
  warnings: string[]
  engine_version: string
}

export interface RouteStep {
  instruction: string
  road_name: string
  distance_m: number
  duration_s: number
  maneuver_type: string
  modifier?: string | null
  location: [number, number]
}

export interface RouteLeg {
  from_label: string
  to_label: string
  distance_km: number
  duration_min: number
  coordinates: [number, number][]
  steps: RouteStep[]
}

export interface RouteResponse {
  provider: string
  total_distance_km: number
  total_duration_min: number
  legs: RouteLeg[]
}

export function formatTariff(val: number | null | undefined): string {
  if (val == null) return 'Unlisted (est. ₹18/kWh)'
  if (val === 0) return 'Free (₹0/kWh)'
  return `₹${val}/kWh`
}

export interface VehicleProfile {
  vehicle_id?: number
  id?: number
  segment: 'E2W' | 'E3W' | 'E4W' | 'ELCV'
  model_name?: string
  make_model?: string
  battery_kwh: number
  wh_per_km: number
  max_dc_kw: number | null
  max_ac_kw: number | null
  connector_types: string[]
  source?: string
  confidence?: number
}

export interface ConnectorDetail {
  connector_id?: number
  station_id?: number
  connector_type: string
  output_power_kw: number
  status?: string
}

export interface StationFeature {
  type: 'Feature'
  geometry: {
    type: 'Point'
    coordinates: [number, number] // [lon, lat]
  }
  properties: {
    station_id: number
    name?: string
    station_name?: string
    cpo_name?: string | null
    address?: string | null
    max_power_kw?: number | null
    tariff_inr_kwh?: number | null
    rating?: number | null
    is_operational?: boolean
    open_24x7?: boolean
    hours_text?: string | null
    connector_types?: string[]
    connectors?: ConnectorDetail[]
    source: string
    source_ref?: string | null
    confidence: number
    fetched_at?: string
  }
}

export interface StationFeatureCollection {
  type: 'FeatureCollection'
  features: StationFeature[]
}

export interface SystemStatusResponse {
  service: string
  phase: string
  database: {
    backend: string
    connected: boolean
    stations_count?: number
    postgres_note?: string
  }
  stations_total: number
  stations_by_source: Record<string, number>
  policy_benchmarks?: {
    mop_guidelines_2022?: {
      urban_grid_km: number
      highway_spacing_km: number
      fast_charger_heavy_duty_spacing_km: number
    }
    mhi_rajya_sabha_q3910_2026_03_27?: {
      omc_stations_installed: number
      omc_stations_operational: number
      operational_ratio_pct: number
    }
  }
}

export interface CensusPayload {
  station_name: string
  cpo_name?: string
  latitude: number
  longitude: number
  address?: string
  max_power_kw?: number
  tariff_inr_kwh?: number
  open_24x7: boolean
  is_operational: boolean
  connectors: { connector_type: string; output_power_kw: number; status: string }[]
  enumerator: string
}

export interface SurveyPayload {
  consent: boolean
  segment: 'E2W' | 'E3W' | 'E4W' | 'ELCV'
  vehicle_model?: string
  area?: string
  home_charging: boolean
  range_anxiety: number
  best_criterion: string
  worst_criterion: string
  best_to_others: Record<string, number>
  others_to_worst: Record<string, number>
  wtp_zero_wait_inr?: number
  enumerator?: string
}

export interface QueuePayload {
  station_id: number
  slot: '07-10' | '12-15' | '18-21'
  vehicles_waiting: number
  connectors_busy: number
  arrivals_in_interval: number
  interval_minutes: number
  observer?: string
}

export const getBaseUrl = (): string => {
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
  getStatus: () => request<SystemStatusResponse>('/v1/status'),

  getModes: () =>
    request<{
      criteria: string[]
      modes: Record<string, number[]>
      descriptions?: Record<string, string>
    }>('/v1/modes'),

  getVehicles: async (): Promise<VehicleProfile[]> => {
    const rows = await request<VehicleProfile[]>('/v1/vehicles')
    return rows.map((v, idx) => ({
      ...v,
      vehicle_id: v.vehicle_id ?? v.id ?? idx + 1,
      model_name: v.model_name ?? v.make_model ?? 'Unknown EV',
    }))
  },

  getStations: (bbox: string, source?: string) => {
    const params = new URLSearchParams({ bbox })
    if (source) params.append('source', source)
    return request<StationFeatureCollection>(`/v1/stations?${params.toString()}`)
  },

  getStationDetail: (id: number) => request<StationFeature['properties']>(`/v1/stations/${id}`),

  recommend: (body: RecommendRequest) =>
    request<RecommendResult>('/v1/recommend', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  getRoute: (body: {
    origin: LatLon
    destination: LatLon
    waypoint?: LatLon | null
    waypoint_name?: string | null
  }) =>
    request<RouteResponse>('/v1/route', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

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

  getExportUrl: (kind: 'census' | 'survey' | 'queue'): string => {
    return `${getBaseUrl()}/v1/field/export/${kind}`
  },
}
