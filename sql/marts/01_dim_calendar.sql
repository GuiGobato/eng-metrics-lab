CREATE OR REPLACE TABLE marts.dim_calendar AS
SELECT
    CAST(d AS DATE) AS date_day,
    CAST(DATE_TRUNC('week', d) AS DATE) AS week_start,
    CAST(DATE_TRUNC('month', d) AS DATE) AS month_start,
    STRFTIME(d, '%Y-%m') AS year_month
FROM GENERATE_SERIES(DATE '2026-04-01', DATE '2026-09-30', INTERVAL 1 DAY) AS t(d);
