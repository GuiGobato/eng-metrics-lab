CREATE OR REPLACE TABLE staging.stg_github_pull_requests AS
SELECT
    CAST(number AS INTEGER) AS pr_number,
    title,
    CAST(CAST(created_at AS TIMESTAMPTZ) AS TIMESTAMP) AS opened_at,
    CAST(CAST(merged_at AS TIMESTAMPTZ) AS TIMESTAMP) AS merged_at,
    merge_commit_sha
FROM raw.github_pull_requests
WHERE merged_at IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY number ORDER BY merged_at) = 1;