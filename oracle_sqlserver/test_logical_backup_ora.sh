#!/bin/bash

export tags_env=dev
export tags_owner=koizumi
export DB_INSTANCE_IDENTIFIER=koizumi-dev-db-oracle-1st
export DB_NAME=MASTERDB
export DB_SCHEMA=XX_ADM
export DB_MASTER=MASTERUSER
export PASSWORD_KEY=oracle
export DB_INSTANCE_CLASS=db.t3.medium
export DB_PORT=1521
export DB_SUBNET_GROUP=koizumi-dev-subnet
export VPC_SECURITY_GROUP_IDS=sg-02dc90cfb43154370
export S3_BUCKET=koizumi-dev-data
export S3_PREFIX=backup/rds/oracle
export S3_INTEGRATION="arn:aws:iam::532973931974:role/koizumi-dev-role-rds"

export koizumi-dev_DBPASSWORD=<<EOF
{
  "mysql": "Admin123!",
  "oracle": "Admin123!",
  "postgresql": "Admin123!",
  "redshift": "Admin123!",
  "sqlserver": "Admin123!"
}
EOF

python3 rds_logical_backup.py
