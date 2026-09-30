CREATE OR REPLACE TABLE staging.stg_github_releases AS
SELECT
    tag_name AS release_tag,
    name AS release_name,
    prerelease AS is_prerelease,
    CAST(CAST(published_at AS TIMESTAMPTZ) AS TIMESTAMP) AS published_at
FROM raw.github_releases
WHERE draft = FALSE
  AND published_at IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY tag_name ORDER BY published_at) = 1;