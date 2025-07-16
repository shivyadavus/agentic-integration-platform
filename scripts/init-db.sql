-- Initialize the Agentic Integration Platform Database
-- This script sets up the initial database structure

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS integrations;
CREATE SCHEMA IF NOT EXISTS knowledge;
CREATE SCHEMA IF NOT EXISTS users;

-- Grant permissions
GRANT USAGE ON SCHEMA integrations TO postgres;
GRANT USAGE ON SCHEMA knowledge TO postgres;
GRANT USAGE ON SCHEMA users TO postgres;

-- Create initial tables will be handled by Alembic migrations
-- This script just sets up the basic database structure

-- Log initialization (pg_stat_statements_info table may not exist)
-- INSERT INTO pg_stat_statements_info (dealloc) VALUES (0) ON CONFLICT DO NOTHING;

-- Database initialization complete
SELECT 'Agentic Integration Platform database initialized successfully' AS status;
