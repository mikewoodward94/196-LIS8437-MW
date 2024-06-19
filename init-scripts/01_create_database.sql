\c csc

SELECT 'Creating schemas...' AS message;
CREATE SCHEMA patient;
CREATE SCHEMA radiology;
SELECT 'Schemas created...' AS message;

SELECT 'Setting search path...' AS message;
SET search_path = patient, radiology, public;
SELECT 'Search path set...' AS message;

SELECT 'Creating tables...' AS message;
CREATE TABLE patient.demographics (
			patient_id VARCHAR(10) NOT NULL,
			nhs_number VARCHAR(10) NOT NULL,
			forename VARCHAR(50) NOT NULL,
			surname VARCHAR(50) NOT NULL,
			dob DATE NOT NULL,
            dod DATE NULL,
            sex VARCHAR(1) NOT NULL,
            sex_description VARCHAR(255) NOT NULL,
            gender VARCHAR(1) NOT NULL,
            gender_description VARCHAR(255) NOT NULL,
            ethnicity VARCHAR(1) NOT NULL,
            ethnicity_description VARCHAR(255) NOT NULL,
			archived BOOLEAN DEFAULT FALSE,
			created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
			modified_date DATE NULL
            );

CREATE TABLE radiology.order_tbl (
			patient_id VARCHAR(10) NOT NULL,
			order_id VARCHAR(36) NOT NULL,
            order_code VARCHAR(6) NOT NULL,
            order_description VARCHAR(10) NOT NULL,
			deleted BOOLEAN DEFAULT FALSE,
			created_date TIMESTAMP NOT NULL,
			modified_date DATE NULL
            );

CREATE TABLE radiology.report (
			patient_id VARCHAR(10) NOT NULL,
			order_id VARCHAR(36) NOT NULL,
            report_id VARCHAR(36) NOT NULL,
			deleted BOOLEAN DEFAULT FALSE,
			created_date TIMESTAMP NOT NULL,
			modified_date DATE NULL
            );
SELECT 'Tables created...' AS message;

SELECT 'Creating primary keys...' AS message;
ALTER TABLE patient.demographics ADD CONSTRAINT pk_patient_demographics PRIMARY KEY (patient_id);
ALTER TABLE radiology.order_tbl ADD CONSTRAINT pk_radiology_order PRIMARY KEY (order_id);
ALTER TABLE radiology.report ADD CONSTRAINT pk_radiology_report PRIMARY KEY (report_id);
SELECT 'Primary keys created...' AS message;

SELECT 'Inserting data...' AS message;
\copy patient.demographics FROM '/docker-entrypoint-initdb.d/data/patient_demographics.csv' DELIMITER ',' CSV HEADER ENCODING 'UTF8' QUOTE '"' ESCAPE '''';
\copy radiology.order_tbl FROM '/docker-entrypoint-initdb.d/data/radiology_order.csv' DELIMITER ',' CSV HEADER ENCODING 'UTF8' QUOTE '"' ESCAPE '''';
\copy radiology.report FROM '/docker-entrypoint-initdb.d/data/radiology_report.csv' DELIMITER ',' CSV HEADER ENCODING 'UTF8' QUOTE '"' ESCAPE '''';
SELECT 'Data inserted...' AS message;