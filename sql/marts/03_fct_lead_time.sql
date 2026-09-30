CREATE OR REPLACE TABLE marts.fct_lead_time AS
SELECT
    pr.pr_number,
    pr.opened_at,
    pr.merged_at,
    d.release_tag,
    d.deployed_at,
    CAST(DATE_TRUNC('week', pr.merged_at) AS DATE) AS week_start,
    DATE_DIFF('minute', pr.opened_at, pr.merged_at) / 60.0 AS hours_to_merge,
    DATE_DIFF('minute', pr.opened_at, d.deployed_at) / 60.0 AS lead_time_hours
FROM staging.stg_github_pull_requests pr
ASOF LEFT JOIN marts.fct_deployments d
    ON pr.merged_at <= d.deployed_at;