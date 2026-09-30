CREATE OR REPLACE TABLE marts.fct_deployments AS
SELECT
    r.release_tag,
    r.published_at AS deployed_at,
    CAST(r.published_at AS DATE) AS deploy_date,
    CAST(DATE_TRUNC('week', r.published_at) AS DATE) AS week_start,
    COUNT(i.incident_id) AS incident_count,
    COUNT(i.incident_id) > 0 AS caused_incident
FROM staging.stg_github_releases r
LEFT JOIN staging.stg_incidents i USING (release_tag)
WHERE r.is_prerelease = FALSE
GROUP BY 1, 2, 3, 4;