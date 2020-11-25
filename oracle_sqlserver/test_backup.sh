#!/bin/bash

# oracle
export tags_env=dev
export tags_owner=koizumi
export DB_INSTANCE_IDENTIFIER=koizumi-dev-db-oracle-1st
export DB_ENDPOINT=koizumi-dev-db-oracle-1st-backup.cp18wjhx9brf.eu-north-1.rds.amazonaws.com
export DB_PORT=1521
export DB_NAME=MASTERDB
export DB_SCHEMA=XX_ADM
export DB_MASTER=MASTERUSER
export PASSWORD_KEY=oracle
export S3_BUCKET=koizumi-dev-data
export S3_PREFIX=backup/rds/oracle
export DB_SELECT=oracle
export koizumi-dev_DBPASSWORD=`cat sample.json | jq`

exit
python3 test_backup.py


# sqlserver
export DB_INSTANCE_IDENTIFIER=koizumi-dev-sqlserver-1st
export DB_ENDPOINT=koizumi-dev-sqlserver-1st-backup.cp18wjhx9brf.eu-north-1.rds.amazonaws.com
export DB_PORT=1433
export DB_NAME=xx00
export DB_MASTER=masteruser
export DB_PASSWORD="Admin123!"
export S3_BUCKET=koizumi-dev-data
export S3_PREFIX=backup/rds/sqlserver
export DB_SELECT=sqlserver

#python3 test_backup.py

