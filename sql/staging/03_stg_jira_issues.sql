CREATE OR REPLACE TABLE staging.stg_jira_issues AS
SELECT
    issue_key,
    team,
    issue_type,
    current_status,
    CAST(CAST(created_at AS TIMESTAMPTZ) AS TIMESTAMP) AS created_at,
    CAST(CAST(done_at AS TIMESTAMPTZ) AS TIMESTAMP) AS done_at
FROM raw.jira_issues;