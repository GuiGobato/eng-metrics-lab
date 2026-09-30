CREATE OR REPLACE TABLE staging.stg_jira_transitions AS
SELECT
    issue_key,
    to_status AS status,
    CASE to_status
        WHEN 'Backlog' THEN 1
        WHEN 'Refinement' THEN 2
        WHEN 'In Progress' THEN 3
        WHEN 'In Review' THEN 4
        WHEN 'QA' THEN 5
        WHEN 'Done' THEN 6
    END AS status_order,
    CAST(CAST(transitioned_at AS TIMESTAMPTZ) AS TIMESTAMP) AS transitioned_at
FROM raw.jira_transitions;