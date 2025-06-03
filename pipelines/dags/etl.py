from airflow import DAG
from airflow.decorators import task
from neo4j import GraphDatabase
from datetime import datetime, timedelta
import requests, pathlib, uuid, os, json

default_args = {"retries": 2, "retry_delay": timedelta(minutes=2)}

with DAG(
    dag_id="etl",
    start_date=datetime(2025, 6, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
) as dag:

    @task
    def extract():
        return requests.get("https://catfact.ninja/fact", timeout=10).json()

    @task
    def transform(raw):
        return raw["fact"].upper()

    @task
    def load(fact: str):
        """
        • Creates one (:Fact) node per run
        • Links it to a single singleton (:Cat {name:'Cat'}) node
        """
        uri  = os.getenv("NEO4J_URI",  "bolt://neo4j:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        pwd  = os.getenv("NEO4J_PWD",  "password")

        driver = GraphDatabase.driver(uri, auth=(user, pwd))

        cypher = """
        MERGE (c:Cat {name:'Cat'})
        CREATE (f:Fact {id:$id, text:$text, created:datetime()})
        CREATE (c)-[:SAYS]->(f)
        """

        with driver.session() as ses:
            ses.execute_write(lambda tx: tx.run(cypher, id=str(uuid.uuid4()), text=fact))
        driver.close()

    load(transform(extract()))
