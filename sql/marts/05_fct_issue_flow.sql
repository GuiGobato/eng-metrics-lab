CREATE OR REPLACE TABLE marts.fct_issue_flow AS
WITH marcos AS (
    SELECT
        issue_key,
        MIN(CASE WHEN status = 'In Progress' THEN transitioned_at END) AS started_at,
        MIN(CASE WHEN status = 'Done' THEN transitioned_at END) AS done_at
    FROM staging.stg_jira_transitions
    GROUP BY 1
)
SELECT
    i.issue_key,
    i.team,
    i.issue_type,
    i.current_status,
    i.created_at,
    m.started_at,
    m.done_at,
    CAST(DATE_TRUNC('week', m.done_at) AS DATE) AS done_week,
    DATE_DIFF('minute', m.started_at, m.done_at) / 60.0 / 24.0 AS cycle_time_days
FROM staging.stg_jira_issues i
LEFT JOIN marcos m USING (issue_key);