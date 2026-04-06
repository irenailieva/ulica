-- SQL initialization script
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE raw_scrapes (
    id SERIAL PRIMARY KEY,
    source_platform VARCHAR(50) NOT NULL,
    external_id VARCHAR(100) UNIQUE,
    raw_text TEXT NOT NULL,
    raw_images JSONB,
    scrape_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'PENDING'
);

CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    raw_scrape_id INTEGER REFERENCES raw_scrapes(id),
    species VARCHAR(50),
    description TEXT,
    urgency_level INTEGER,
    location_point GEOMETRY(Point, 4326),
    location_area GEOMETRY(Polygon, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signals_area ON signals USING GIST (location_area);