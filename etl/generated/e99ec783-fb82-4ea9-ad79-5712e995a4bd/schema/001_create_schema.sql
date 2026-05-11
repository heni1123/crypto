CREATE SCHEMA IF NOT EXISTS manual;
COMMENT ON SCHEMA manual IS 'Schema for ETL pipeline to store cryptocurrency market snapshots';
GRANT ALL PRIVILEGES ON SCHEMA manual TO your_etl_user;