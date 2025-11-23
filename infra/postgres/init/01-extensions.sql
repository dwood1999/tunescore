-- TuneScore PostgreSQL Extensions Initialization
-- This script runs automatically when the PostgreSQL container is first created

-- Enable required extensions for TuneScore
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";           -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";             -- Trigram matching for fuzzy search
CREATE EXTENSION IF NOT EXISTS "vector";              -- pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";  -- Query performance monitoring
CREATE EXTENSION IF NOT EXISTS "btree_gin";           -- GIN indexes for better performance
CREATE EXTENSION IF NOT EXISTS "btree_gist";          -- GIST indexes for better performance

-- Optional: PostGIS for geographic data (if needed for tour routing, venue locations)
-- CREATE EXTENSION IF NOT EXISTS "postgis";

-- Create schema for better organization (optional)
-- CREATE SCHEMA IF NOT EXISTS music;
-- CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE tunescore TO tunescore;

-- Set up optimal settings for the application
ALTER DATABASE tunescore SET timezone TO 'UTC';
ALTER DATABASE tunescore SET default_text_search_config TO 'pg_catalog.english';

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'TuneScore database extensions initialized successfully';
END $$;

