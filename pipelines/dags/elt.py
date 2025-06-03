from airflow import DAG
from airflow.decorators import task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd

with DAG(
    dag_id="elt",
    start_date=datetime(2025, 6, 1),
    schedule="@daily",
    catchup=False,
    tags=["elt", "postgres"],
) as dag:

    @task
    def extract():
        url = "https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()  # ← remove leading/trailing spaces
        return df.to_dict(orient="records")

    @task
    def load(records):
        hook = PostgresHook(postgres_conn_id="pg")
        conn = hook.get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS air_raw (
                month TEXT PRIMARY KEY,
                y1958 INTEGER,
                y1959 INTEGER,
                y1960 INTEGER
            )
        """)
        for row in records:
            cur.execute(
                "INSERT INTO air_raw (month, y1958, y1959, y1960) VALUES (%s, %s, %s, %s) ON CONFLICT (month) DO NOTHING",                
                (row["Month"], row['"1958"'], row['"1959"'], row['"1960"'])
            )
        conn.commit()

    transform = SQLExecuteQueryOperator(
        task_id="transform",
        conn_id="pg",
        sql="""
            CREATE TABLE IF NOT EXISTS air_summary AS
            SELECT
                month,
                (y1958 + y1959 + y1960) AS total_passengers
            FROM air_raw
        """
    )

    load(extract()) >> transform