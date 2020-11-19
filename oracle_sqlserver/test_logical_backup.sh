#!/bin/bash

export tags_env=dev
export tags_owner=koizumi
export DB_INSTANCE_IDENTIFIER=koizumi-dev-db-oracle-1st
export DB_NAME=MASTERDB
export DB_SCHEMA=XX_ADM
export DB_MASTER=MASTERUSER
export DB_PASSWORD="Admin123!"
export DB_INSTANCE_CLASS=db.t3.medium
export DB_SUBNET_GROUP=koizumi-dev-subnet
export DB_OPTION_GROUP=koizumi-dev-opg-oracle-1st
export DB_PORT=1521
export VPC_SECURITY_GROUP_IDS=sg-02dc90cfb43154370
export S3_BUCKET=koizumi-dev-data
export S3_PREFIX=backup/rds/oracle


python3 rds_logical_backup.py
