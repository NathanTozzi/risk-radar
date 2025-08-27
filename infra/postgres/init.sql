-- PostgreSQL initialization script
-- This runs when the database container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance (will be created by SQLModel too, but good to have)
-- These will be created by the application, but we can pre-create some for better performance

-- Initial data will be seeded by the application using the seed script