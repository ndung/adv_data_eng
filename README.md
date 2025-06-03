# adv_data_eng

cd pipelines

docker-compose up -d

open http://localhost:8080/connections

Create connections:

1. id: pg, type: postgres, host: postgres, username: airflow, password: airflow, port: 5432, database: airflow

2. id: neo4j_default, type: generic, host: neo4j, login: neo4j, password: password, port: 7687, scheme: {"scheme":"bolt"}
