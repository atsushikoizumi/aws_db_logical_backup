#!/bin/bash

# sqlserver
export DB_IDENTIFIER=koizumi-dev-sqlserver-1st
export DB_ENDPOINT=koizumi-dev-sqlserver-1st.cp18wjhx9brf.eu-north-1.rds.amazonaws.com
export DB_PORT=1433
export DB_NAME=xx00
export DB_USER=masteruser
export DB_PASSWORD="Admin123!"
export S3_BUCKET=koizumi-dev-data
export S3_PREFIX=backup/rds/sqlserver/koizumi-dev-sqlserver-1st
export DB_SELECT=sqlserver

python3 test_backup.py


# oracle
export DB_IDENTIFIER=koizumi-dev-db-oracle-1st
export DB_ENDPOINT=koizumi-dev-db-oracle-1st.cp18wjhx9brf.eu-north-1.rds.amazonaws.com
export DB_PORT=1521
export DB_NAME=MASTERDB
export DB_SCHEMA=XX_ADM
export DB_USER=MASTERUSER
export DB_PASSWORD="Admin123!"
export S3_BUCKET=koizumi-dev-data
export S3_PREFIX=backup/rds/oracle/koizumi-dev-db-oracle-1st
export DB_SELECT=oracle

python3 test_backup.py
