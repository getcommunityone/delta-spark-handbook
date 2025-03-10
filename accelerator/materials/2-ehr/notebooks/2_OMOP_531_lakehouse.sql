-- Drop existing database if it exists
DROP DATABASE IF EXISTS OMOP531 CASCADE;
CREATE DATABASE IF NOT EXISTS OMOP531 LOCATION '/path/to/delta_silver_path';
USE OMOP531;

-- Create tables
CREATE OR REPLACE TABLE CONCEPT (
  CONCEPT_ID LONG,
  CONCEPT_NAME STRING,
  DOMAIN_ID STRING,
  VOCABULARY_ID STRING,
  CONCEPT_CLASS_ID STRING,
  STANDARD_CONCEPT STRING,
  CONCEPT_CODE STRING,
  VALID_START_DATE DATE,
  VALID_END_DATE DATE,
  INVALID_REASON STRING
) USING DELTA;

CREATE OR REPLACE TABLE VOCABULARY (
  VOCABULARY_ID STRING,
  VOCABULARY_NAME STRING,
  VOCABULARY_REFERENCE STRING,
  VOCABULARY_VERSION STRING,
  VOCABULARY_CONCEPT_ID LONG
) USING DELTA;

CREATE OR REPLACE TABLE DOMAIN (
  DOMAIN_ID STRING,
  DOMAIN_NAME STRING,
  DOMAIN_CONCEPT_ID LONG
) USING DELTA;

CREATE OR REPLACE TABLE CONCEPT_CLASS (
  CONCEPT_CLASS_ID STRING,
  CONCEPT_CLASS_NAME STRING,
  CONCEPT_CLASS_CONCEPT_ID LONG
) USING DELTA;

CREATE OR REPLACE TABLE CONCEPT_RELATIONSHIP (
  CONCEPT_ID_1 LONG,
  CONCEPT_ID_2 LONG,
  RELATIONSHIP_ID STRING,
  VALID_START_DATE DATE,
  VALID_END_DATE DATE,
  INVALID_REASON STRING
) USING DELTA;

CREATE OR REPLACE TABLE RELATIONSHIP (
  RELATIONSHIP_ID STRING,
  RELATIONSHIP_NAME STRING,
  IS_HIERARCHICAL STRING,
  DEFINES_ANCESTRY STRING,
  REVERSE_RELATIONSHIP_ID STRING,
  RELATIONSHIP_CONCEPT_ID LONG
) USING DELTA;

CREATE OR REPLACE TABLE CONCEPT_SYNONYM (
  CONCEPT_ID LONG,
  CONCEPT_SYNONYM_NAME STRING,
  LANGUAGE_CONCEPT_ID LONG
) USING DELTA;

CREATE OR REPLACE TABLE CONCEPT_ANCESTOR (
  ANCESTOR_CONCEPT_ID LONG,
  DESCENDANT_CONCEPT_ID LONG,
  MIN_LEVELS_OF_SEPARATION LONG,
  MAX_LEVELS_OF_SEPARATION LONG
) USING DELTA;

CREATE OR REPLACE TABLE SOURCE_TO_CONCEPT_MAP (
  SOURCE_CODE STRING,
  SOURCE_CONCEPT_ID LONG,
  SOURCE_VOCABULARY_ID STRING,
  SOURCE_CODE_DESCRIPTION STRING,
  TARGET_CONCEPT_ID LONG,
  TARGET_VOCABULARY_ID STRING,
  VALID_START_DATE DATE,
  VALID_END_DATE DATE,
  INVALID_REASON STRING
) USING DELTA;

CREATE OR REPLACE TABLE DRUG_STRENGTH (
  DRUG_CONCEPT_ID LONG,
  INGREDIENT_CONCEPT_ID LONG,
  AMOUNT_VALUE DOUBLE,
  AMOUNT_UNIT_CONCEPT_ID LONG,
  NUMERATOR_VALUE DOUBLE,
  NUMERATOR_UNIT_CONCEPT_ID LONG,
  DENOMINATOR_VALUE DOUBLE,
  DENOMINATOR_UNIT_CONCEPT_ID LONG,
  BOX_SIZE LONG,
  VALID_START_DATE DATE,
  VALID_END_DATE DATE,
  INVALID_REASON STRING
) USING DELTA;

CREATE OR REPLACE TABLE ATTRIBUTE_DEFINITION (
  ATTRIBUTE_DEFINITION_ID LONG,
  ATTRIBUTE_NAME STRING,
  ATTRIBUTE_DESCRIPTION STRING,
  ATTRIBUTE_TYPE_CONCEPT_ID LONG,
  ATTRIBUTE_SYNTAX STRING
) USING DELTA;

CREATE OR REPLACE TABLE CDM_SOURCE (
  CDM_SOURCE_NAME STRING,
  CDM_SOURCE_ABBREVIATION STRING,
  CDM_HOLDER STRING,
  SOURCE_DESCRIPTION STRING,
  SOURCE_DOCUMENTATION_REFERENCE STRING,
  CDM_ETL_REFERENCE STRING,
  SOURCE_RELEASE_DATE DATE,
  CDM_RELEASE_DATE DATE,
  CDM_VERSION STRING,
  VOCABULARY_VERSION STRING
) USING DELTA;

CREATE OR REPLACE TABLE METADATA (
  METADATA_CONCEPT_ID LONG,
  METADATA_TYPE_CONCEPT_ID LONG,
  NAME STRING,
  VALUE_AS_STRING STRING,
  VALUE_AS_CONCEPT_ID LONG,
  METADATA_DATE DATE,
  METADATA_DATETIME TIMESTAMP
) USING DELTA;

CREATE OR REPLACE TABLE PERSON (
  PERSON_ID LONG,
  GENDER_CONCEPT_ID LONG,
  YEAR_OF_BIRTH LONG,
  MONTH_OF_BIRTH LONG,
  DAY_OF_BIRTH LONG,
  BIRTH_DATETIME TIMESTAMP,
  RACE_CONCEPT_ID LONG,
  ETHNICITY_CONCEPT_ID LONG,
  LOCATION_ID LONG,
  PROVIDER_ID LONG,
  CARE_SITE_ID LONG,
  PERSON_SOURCE_VALUE STRING,
  GENDER_SOURCE_VALUE STRING,
  GENDER_SOURCE_CONCEPT_ID LONG,
  RACE_SOURCE_VALUE STRING,
  RACE_SOURCE_CONCEPT_ID LONG,
  ETHNICITY_SOURCE_VALUE STRING,
  ETHNICITY_SOURCE_CONCEPT_ID LONG
) USING DELTA;

CREATE OR REPLACE TABLE OBSERVATION_PERIOD (
  OBSERVATION_PERIOD_ID LONG,
  PERSON_ID LONG,
  OBSERVATION_PERIOD_START_DATE DATE,
  OBSERVATION_PERIOD_END_DATE DATE,
  PERIOD_TYPE_CONCEPT_ID LONG
) USING DELTA;

CREATE OR REPLACE TABLE VISIT_OCCURRENCE (
  VISIT_OCCURRENCE_ID LONG,
  PERSON_ID LONG,
  VISIT_CONCEPT_ID LONG,
  VISIT_START_DATE DATE,
  VISIT_START_DATETIME TIMESTAMP,
  VISIT_END_DATE DATE,
  VISIT_END_DATETIME TIMESTAMP,
  VISIT_TYPE_CONCEPT_ID LONG,
  PROVIDER_ID LONG,
  CARE_SITE_ID LONG,
  VISIT_SOURCE_VALUE STRING,
  VISIT_SOURCE_CONCEPT_ID LONG,
  ADMITTING_SOURCE_CONCEPT_ID LONG,
  ADMITTING_SOURCE_VALUE STRING,
  DISCHARGE_TO_CONCEPT_ID LONG,
  DISCHARGE_TO_SOURCE_VALUE STRING,
  PRECEDING_VISIT_OCCURRENCE_ID LONG
) USING DELTA;

CREATE OR REPLACE TABLE CONDITION_OCCURRENCE (
  CONDITION_OCCURRENCE_ID LONG,
  PERSON_ID LONG,
  CONDITION_CONCEPT_ID LONG,
  CONDITION_START_DATE DATE,
  CONDITION_START_DATETIME TIMESTAMP,
  CONDITION_END_DATE DATE,
  CONDITION_END_DATETIME TIMESTAMP,
  CONDITION_TYPE_CONCEPT_ID LONG,
  STOP_REASON STRING,
  PROVIDER_ID LONG,
  VISIT_OCCURRENCE_ID LONG,
  VISIT_DETAIL_ID LONG,
  CONDITION_SOURCE_VALUE STRING,
  CONDITION_SOURCE_CONCEPT_ID LONG,
  CONDITION_STATUS_SOURCE_VALUE STRING,
  CONDITION_STATUS_CONCEPT_ID LONG
) USING DELTA;

-- Insert metadata
INSERT INTO METADATA
VALUES
  (
    0,
    0,
    'OHDSI OMOP CDM Version',
    '5.3.1',
    0,
    CURRENT_DATE(),
    CURRENT_TIMESTAMP()
  );

-- Select metadata
SELECT
  metadata_concept_id,
  metadata_type_concept_id,
  name,
  value_as_string,
  value_as_concept_id,
  metadata_date,
  metadata_datetime
FROM METADATA;
