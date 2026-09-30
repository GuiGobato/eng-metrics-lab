CREATE OR REPLACE TABLE staging.stg_incidents AS
SELECT
    incident_id,
    release_tag,
    severity,
    CAST(CAST(opened_at AS TIMESTAMPTZ) AS TIMESTAMP) AS opened_at,
    CAST(CAST(resolved_at AS TIMESTAMPTZ) AS TIMESTAMP) AS resolved_at
FROM raw.incidents;
