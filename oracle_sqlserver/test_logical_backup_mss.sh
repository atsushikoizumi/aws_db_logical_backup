#!/bin/bash

export tags_env=dev
export tags_owner=koizumi
export DB_INSTANCE_IDENTIFIER=koizumi-dev-sqlserver-1st
export DB_NAME=xx00
export DB_MASTER=masteruser
export PASSWORD_KEY=sqlserver
export DB_INSTANCE_CLASS=db.r5.large
export DB_PORT=1433
export DB_SUBNET_GROUP=koizumi-dev-subnet
export VPC_SECURITY_GROUP_IDS=sg-02dc90cfb43154370
export S3_BUCKET=koizumi-dev-data
export S3_PREFIX=backup/rds/sqlserver

python3 rds_logical_backup.py
