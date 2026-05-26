-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;

-- Create cats table
CREATE TABLE IF NOT EXISTS cats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_seen_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'unverified',
    tnr_status BOOLEAN DEFAULT FALSE
);

-- Create sightings table
CREATE TABLE IF NOT EXISTS sightings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cat_id UUID REFERENCES cats(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    location GEOMETRY(Point, 4326),
    image_url TEXT
);

-- Create cat_embeddings table
CREATE TABLE IF NOT EXISTS cat_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sighting_id UUID REFERENCES sightings(id),
    cat_id UUID REFERENCES cats(id),
    embedding VECTOR(512)
);

-- Indexes for fast geospatial and vector search
CREATE INDEX IF NOT EXISTS sightings_location_idx ON sightings USING GIST (location);
CREATE INDEX IF NOT EXISTS cat_embeddings_embedding_idx ON cat_embeddings USING hnsw (embedding vector_cosine_ops);
