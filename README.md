# adv_data_eng

cd pipelines

docker-compose up -d

Open http://localhost:8080/connections username: airflow, password: airflow

Create connections:

1. id: pg, type: postgres, host: postgres, username: airflow, password: airflow, port: 5432, database: airflow

2. id: neo4j_default, type: generic, host: neo4j, login: neo4j, password: password, port: 7687, scheme: {"scheme":"bolt"}

Run elt and etl in http://localhost:8080/dags

Open http://localhost:7474/ to query neo4j database
