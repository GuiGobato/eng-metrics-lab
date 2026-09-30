import duckdb

con = duckdb.connect()
print(con.sql("SELECT 'DuckDB funcionando!' AS status").fetchall())