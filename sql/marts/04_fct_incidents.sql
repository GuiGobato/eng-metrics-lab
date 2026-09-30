CREATE OR REPLACE TABLE marts.fct_incidents AS
SELECT
    incident_id,
    release_tag,
    severity,
    opened_at,
    resolved_at,
    CAST(DATE_TRUNC('month', opened_at) AS DATE) AS month_start,
    CAST(DATE_TRUNC('week', opened_at) AS DATE) AS week_start,
    DATE_DIFF('minute', opened_at, resolved_at) / 60.0 AS hours_to_restore
FROM staging.stg_incidents;