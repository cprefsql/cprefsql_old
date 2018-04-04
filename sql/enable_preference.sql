-- Module "postgresql-plpython" is required

-- Drop existent content
DROP TABLE IF EXISTS __preferences; 
DROP EXTENSION IF EXISTS plpythonu CASCADE;

-- Extension required
CREATE EXTENSION plpythonu;

-- Table to store preferences
CREATE TABLE __preferences(
    preference_name TEXT PRIMARY KEY,
    preference_rules TEXT);
