from pathlib import Path

import duckdb

DB_PATH = Path("data/warehouse.duckdb")
RAW = Path("data/raw")
SQL_DIRS = ["sql/staging"]


def path_sql(name):
    return (RAW / name).as_posix()


def load_raw(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    # Só as colunas necessárias. O campo "user" (pessoas) fica de fora de propósito.
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.github_pull_requests AS
        SELECT number, title, created_at, merged_at, merge_commit_sha
        FROM read_json_auto('{path_sql("github_pull_requests.json")}')
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.github_releases AS
        SELECT tag_name, name, draft, prerelease, published_at
        FROM read_json_auto('{path_sql("github_releases.json")}')
    """)

    for name in ["jira_issues", "jira_transitions", "incidents"]:
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.{name} AS
            SELECT * FROM read_csv('{path_sql(name + ".csv")}', header=true, all_varchar=true)
        """)


def run_sql_folder(con, folder):
    for f in sorted(Path(folder).glob("*.sql")):
        print(f"  executando {f}")
        con.execute(f.read_text(encoding="utf-8"))


def main():
    con = duckdb.connect(str(DB_PATH))
    con.execute("SET TimeZone = 'UTC'")

    print("Carregando raw...")
    load_raw(con)

    con.execute("CREATE SCHEMA IF NOT EXISTS staging")
    for folder in SQL_DIRS:
        print(f"Rodando {folder}...")
        run_sql_folder(con, folder)

    print("Pronto:", DB_PATH)
    con.close()


if __name__ == "__main__":
    main()