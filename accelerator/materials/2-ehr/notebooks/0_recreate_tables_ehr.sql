-- SQL Script to recreate tables from MinIO warehouse: s3a://wba/warehouse
-- Database: ehr

CREATE DATABASE IF NOT EXISTS ehr;

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.allergies;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.allergies
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/allergies';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.careplans;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.careplans
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/careplans';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.claims;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.claims
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/claims';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.claims_transactions;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.claims_transactions
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/claims_transactions';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.conditions;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.conditions
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/conditions';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.devices;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.devices
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/devices';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.encounters;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.encounters
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/encounters';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.imaging_studies;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.imaging_studies
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/imaging_studies';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.immunizations;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.immunizations
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/immunizations';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.medications;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.medications
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/medications';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.observations;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.observations
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/observations';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.organizations;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.organizations
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/organizations';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.patients;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.patients
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/patients';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.payer_transitions;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.payer_transitions
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/payer_transitions';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.payers;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.payers
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/payers';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.procedures;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.procedures
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/procedures';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.providers;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.providers
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/providers';

-- Drop table if it exists
DROP TABLE IF EXISTS ehr.supplies;

-- Create Delta table pointing to existing data
CREATE TABLE ehr.supplies
USING DELTA
LOCATION 's3a://wba/warehouse/ehr.db/supplies';

