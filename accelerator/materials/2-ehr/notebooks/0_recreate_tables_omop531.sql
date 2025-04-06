-- SQL Script to recreate tables from MinIO warehouse: s3a://wba/warehouse
-- Database: omop531

CREATE DATABASE IF NOT EXISTS omop531;

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.attribute_definition;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.attribute_definition
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/attribute_definition';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.care_site;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.care_site
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/care_site';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.cdm_source;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.cdm_source
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/cdm_source';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.cohort;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.cohort
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/cohort';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.cohort_attribute;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.cohort_attribute
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/cohort_attribute';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.cohort_definition;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.cohort_definition
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/cohort_definition';

-- Table concept already exists
-- Drop table if it exists
DROP TABLE IF EXISTS omop531.concept;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.concept
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/concept';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.concept_ancestor;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.concept_ancestor
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/concept_ancestor';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.concept_class;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.concept_class
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/concept_class';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.concept_relationship;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.concept_relationship
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/concept_relationship';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.concept_synonym;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.concept_synonym
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/concept_synonym';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.condition_era;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.condition_era
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/condition_era';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.condition_occurrence;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.condition_occurrence
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/condition_occurrence';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.cost;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.cost
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/cost';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.death;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.death
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/death';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.device_exposure;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.device_exposure
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/device_exposure';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.domain;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.domain
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/domain';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.dose_era;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.dose_era
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/dose_era';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.drug_era;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.drug_era
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/drug_era';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.drug_exposure;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.drug_exposure
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/drug_exposure';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.drug_strength;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.drug_strength
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/drug_strength';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.fact_relationship;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.fact_relationship
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/fact_relationship';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.location;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.location
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/location';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.measurement;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.measurement
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/measurement';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.metadata;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.metadata
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/metadata';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.note;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.note
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/note';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.note_nlp;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.note_nlp
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/note_nlp';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.observation;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.observation
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/observation';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.observation_period;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.observation_period
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/observation_period';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.payer_plan_period;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.payer_plan_period
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/payer_plan_period';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.person;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.person
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/person';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.procedure_occurrence;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.procedure_occurrence
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/procedure_occurrence';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.provider;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.provider
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/provider';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.relationship;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.relationship
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/relationship';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.source_to_concept_map;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.source_to_concept_map
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/source_to_concept_map';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.specimen;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.specimen
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/specimen';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.visit_detail;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.visit_detail
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/visit_detail';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.visit_occurrence;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.visit_occurrence
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/visit_occurrence';

-- Drop table if it exists
DROP TABLE IF EXISTS omop531.vocabulary;

-- Create Delta table pointing to existing data
CREATE TABLE omop531.vocabulary
USING DELTA
LOCATION 's3a://wba/warehouse/omop531.db/vocabulary';

