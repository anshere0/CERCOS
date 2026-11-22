-- CERCOS database contract (PostgreSQL 16 + PostGIS). Owner of the Alembic migration: Ansh. Reviewer: Yash.
-- Any change to this file needs approval from BOTH Ansh and Yash (see CODEOWNERS).
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE SCHEMA IF NOT EXISTS cercos;

CREATE TABLE cercos.districts (
  district_id SERIAL PRIMARY KEY,
  district_name VARCHAR(100) NOT NULL UNIQUE,
  rto_code VARCHAR(10),
  is_model_ev_city BOOLEAN DEFAULT FALSE,
  ev_total INT, ev_e2w INT, ev_e3w INT, ev_e4w INT, ev_other INT,
  ev_data_year INT,
  geom GEOMETRY(MultiPolygon, 4326),
  source VARCHAR(100) NOT NULL, fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(), confidence NUMERIC(3,2) CHECK (confidence BETWEEN 0 AND 1)
);

CREATE TABLE cercos.charging_stations (
  station_id SERIAL PRIMARY KEY,
  cpo_name VARCHAR(100),
  station_name VARCHAR(150) NOT NULL,
  district_id INT REFERENCES cercos.districts(district_id),
  address TEXT,
  max_power_kw NUMERIC(6,2),
  tariff_inr_kwh NUMERIC(5,2),
  rating NUMERIC(2,1) CHECK (rating BETWEEN 1 AND 5),
  is_operational BOOLEAN,
  open_24x7 BOOLEAN,
  hours_text VARCHAR(100),
  contact VARCHAR(100),
  geom GEOMETRY(Point, 4326) NOT NULL,
  source VARCHAR(30) NOT NULL CHECK (source IN ('osm','ocm','census','fixture','synthetic','manual')),
  source_ref VARCHAR(200),
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  confidence NUMERIC(3,2) NOT NULL CHECK (confidence BETWEEN 0 AND 1)
);

CREATE TABLE cercos.connectors (
  connector_id SERIAL PRIMARY KEY,
  station_id INT NOT NULL REFERENCES cercos.charging_stations(station_id) ON DELETE CASCADE,
  connector_type VARCHAR(30) NOT NULL,   -- CCS2, CHAdeMO, Type2, Bharat_AC001, Bharat_DC001, LECCS, GBT, SWAP
  output_power_kw NUMERIC(6,2) NOT NULL,
  status VARCHAR(20) DEFAULT 'UNKNOWN' CHECK (status IN ('AVAILABLE','OCCUPIED','FAULTY','OFFLINE','UNKNOWN'))
);

CREATE TABLE cercos.vehicles (
  vehicle_id SERIAL PRIMARY KEY,
  model_name VARCHAR(100) NOT NULL,
  segment VARCHAR(10) NOT NULL CHECK (segment IN ('E2W','E3W','E4W','ELCV')),
  battery_kwh NUMERIC(6,2), wh_per_km NUMERIC(6,1),
  max_dc_kw NUMERIC(6,2), max_ac_kw NUMERIC(6,2),
  connector_types TEXT[],
  source VARCHAR(100) NOT NULL, confidence NUMERIC(3,2) NOT NULL
);

-- Field research tables (anonymous: NO names, phones or photos of people)
CREATE TABLE cercos.survey_responses (
  response_id SERIAL PRIMARY KEY,
  collected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  segment VARCHAR(10) NOT NULL, vehicle_model VARCHAR(100), area VARCHAR(60),
  home_charging BOOLEAN, range_anxiety SMALLINT CHECK (range_anxiety BETWEEN 1 AND 5),
  best_criterion VARCHAR(20) NOT NULL, worst_criterion VARCHAR(20) NOT NULL,
  best_to_others JSONB NOT NULL,   -- {"cost":3,"wait":5,...} scale 1-9
  others_to_worst JSONB NOT NULL,
  wtp_zero_wait_inr NUMERIC(6,2), consent BOOLEAN NOT NULL CHECK (consent = TRUE),
  enumerator VARCHAR(40)
);

CREATE TABLE cercos.station_observations (
  obs_id SERIAL PRIMARY KEY,
  station_id INT NOT NULL REFERENCES cercos.charging_stations(station_id),
  observed_at TIMESTAMPTZ NOT NULL, slot VARCHAR(10) CHECK (slot IN ('07-10','12-15','18-21')),
  vehicles_waiting SMALLINT, connectors_busy SMALLINT, arrivals_in_interval SMALLINT, interval_minutes SMALLINT,
  session_start TIMESTAMPTZ, session_end TIMESTAMPTZ, kwh_delivered NUMERIC(6,2), observer VARCHAR(40)
);

CREATE TABLE cercos.recommendations_log (
  rec_id BIGSERIAL PRIMARY KEY, created_at TIMESTAMPTZ DEFAULT now(),
  request JSONB NOT NULL, response JSONB NOT NULL, mode VARCHAR(20), engine_version VARCHAR(20)
);

CREATE TABLE cercos.etl_rejects (
  reject_id SERIAL PRIMARY KEY, job VARCHAR(40), raw JSONB, reason TEXT, created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_districts_geom ON cercos.districts USING GIST(geom);
CREATE INDEX idx_stations_geom  ON cercos.charging_stations USING GIST(geom);
