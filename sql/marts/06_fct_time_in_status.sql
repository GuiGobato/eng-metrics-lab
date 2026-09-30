CREATE OR REPLACE TABLE marts.fct_time_in_status AS
WITH ordered AS (
    SELECT
        t.issue_key,
        i.team,
        t.status,
        t.transitioned_at AS entered_at,
        LEAD(t.transitioned_at) OVER (PARTITION BY t.issue_key ORDER BY t.status_order) AS left_at
    FROM staging.stg_jira_transitions t
    JOIN staging.stg_jira_issues i USING (issue_key)
)
SELECT
    issue_key,
    team,
    status,
    entered_at,
    left_at,
    DATE_DIFF('minute', entered_at, left_at) / 60.0 AS hours_in_status
FROM ordered
WHERE left_at IS NOT NULL;