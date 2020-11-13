#!/bin/bash

#
# ver1.5
#
# [task difinittion env]
#  以下の環境変数を設定してタスク定義を作成してください。
#  DBクラスターの数だけタスク定義を作成する必要があります。
export tags_owner=koizumi
export tags_env=dev
export DB_CLUSTER_IDENTIFIER=koizumi-dev-cls-aurora-mysql-1st
export DB_NAME=xx00
export DB_MASTER=masteruser
export PASSWORD_KEY=mysql
export DB_INSTANCE_CLASS=db.t3.medium
export DB_SUBNET_GROUP=koizumi-dev-subnet
export DB_PORT=5432
export VPC_SECURITY_GROUP_IDS=sg-02dc90cfb43154370
export S3_BUCKET=koizumi-dev-data
export S3_PREFIX=backup/rds/mysql
export koizumi_dev_DBPASSWORD=`cat /root/sample.json`
#
# [secret manager]
#  環境変数 "${owner_tags}_${env_tags}_DBPASSWORD" を secret manager から受け取るようタスク定義を設定します。
#  secret manager のシークレット名は "${owner_tags}_${env_tags}_DBPASSWORD" で固定です。
#  シークレットの中身は以下のように key value 形式で設定しています。
#    key           value
#    postgresql    password
#    mysql         password
#  このパスワードは、環境設定ファイル（terraform.tfvars）のパスワードを参照しています。
#  環境変数 PASSWORD_KEY=${key} を指定してください。
#
SECRET_NAME=`echo ${tags_owner}_${tags_env}_DBPASSWORD`
echo $SECRET_NAME
echo ${!SECRET_NAME}
echo ${!SECRET_NAME} | jq -r .${PASSWORD_KEY}
exit

# restore cluster
DB_CLUSTER_IDENTIFIER_RESTORE=${DB_CLUSTER_IDENTIFIER}-backup
DB_CLUSTER_IDENTIFIER_FINAL=${DB_CLUSTER_IDENTIFIER}-final
DB_INSTANCE_IDENTIFIER_RESTORE=${DB_CLUSTER_IDENTIFIER}-backup-01
DATE_TIME=`date +%Y%m%d%H%M%S`
DUMP_FILE=${DB_CLUSTER_IDENTIFIER}_${DB_NAME}_${DATE_TIME}.dmp

# start
echo "====================="
echo "===     start     ==="
echo "====================="

# empty end
if [ -z "${DB_CLUSTER_IDENTIFIER}" ]; then
    date "+[%Y-%m-%d %H:%M:%S] [ERROR] please set DB_CLUSTER_IDENTIFIER."
    exit
fi

# describe-db-clusters
echo "aws rds describe-db-clusters --db-cluster-identifier ${DB_CLUSTER_IDENTIFIER}"
DESCRIBE_DB_CLUSTERS=`aws rds describe-db-clusters --db-cluster-identifier ${DB_CLUSTER_IDENTIFIER}`
if [ $? != 0 ]; then
    date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running describe-db-clusters."
    exit
else
    echo $DESCRIBE_DB_CLUSTERS
    ENGINE=`echo $DESCRIBE_DB_CLUSTERS | jq -r .[][].Engine`
    ENGINE_VERSION=`echo $DESCRIBE_DB_CLUSTERS | jq -r .[][].EngineVersion`
    DB_CLUSTER_PARAMETER_GROUP=`echo $DESCRIBE_DB_CLUSTERS | jq -r .[][].DBClusterParameterGroup`
fi

# describe-db-cluster-snapshots
echo "aws rds describe-db-cluster-snapshots --db-cluster-identifier ${DB_CLUSTER_IDENTIFIER} | jq -r .DBClusterSnapshots[].DBClusterSnapshotIdentifier | sort -r"
DB_CLUSTER_SNAPSHOT_IDENTIFIERS=`aws rds describe-db-cluster-snapshots --db-cluster-identifier "${DB_CLUSTER_IDENTIFIER}" | jq -r .DBClusterSnapshots[].DBClusterSnapshotIdentifier | sort -r`
if [ $? != 0 ]; then
    date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running describe-db-cluster-snapshots."
    exit
elif [ -z "${DB_CLUSTER_SNAPSHOT_IDENTIFIERS}" ]; then
    date "+[%Y-%m-%d %H:%M:%S] [WARNING] there is no snapshot."
    exit
else
    echo $DB_CLUSTER_SNAPSHOT_IDENTIFIERS
fi

# string to array
DB_CLUSTER_SNAPSHOT_IDENTIFIERS=($(echo "${DB_CLUSTER_SNAPSHOT_IDENTIFIERS}")) 
DB_CLUSTER_SNAPSHOT_IDENTIFIER=`echo ${DB_CLUSTER_SNAPSHOT_IDENTIFIERS[0]}`

# restore-db-cluster-from-snapshot
cat <<EOF
aws rds restore-db-cluster-from-snapshot \
    --db-cluster-identifier "$DB_CLUSTER_IDENTIFIER_RESTORE" \
    --snapshot-identifier "$DB_CLUSTER_SNAPSHOT_IDENTIFIER" \
    --db-cluster-parameter-group-name "$DB_CLUSTER_PARAMETER_GROUP" \
    --engine "$ENGINE" \
    --engine-version "$ENGINE_VERSION" \
    --db-subnet-group-name "$DB_SUBNET_GROUP" \
    --port "$DB_PORT" \
    --vpc-security-group-ids "$VPC_SECURITY_GROUP_IDS"
EOF
RESTORE_DB_CLUSTER=`aws rds restore-db-cluster-from-snapshot \
    --db-cluster-identifier "$DB_CLUSTER_IDENTIFIER_RESTORE" \
    --snapshot-identifier "$DB_CLUSTER_SNAPSHOT_IDENTIFIER" \
    --db-cluster-parameter-group-name "$DB_CLUSTER_PARAMETER_GROUP" \
    --engine "$ENGINE" \
    --engine-version "$ENGINE_VERSION" \
    --db-subnet-group-name "$DB_SUBNET_GROUP" \
    --port "$DB_PORT" \
    --vpc-security-group-ids "$VPC_SECURITY_GROUP_IDS"`
if [ $? != 0 ]; then
    date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running restore-db-cluster-from-snapshot."
    exit
else
    echo $RESTORE_DB_CLUSTER
fi

# polling cluster status
status=""
echo "aws rds describe-db-clusters --db-cluster-identifier $DB_CLUSTER_IDENTIFIER_RESTORE | jq -r .DBClusters[].Status"
while [ "available" != "$status" ]
do
    status=`aws rds describe-db-clusters --db-cluster-identifier "$DB_CLUSTER_IDENTIFIER_RESTORE" | jq -r .DBClusters[].Status`
    date "+[%Y-%m-%d %H:%M:%S] $status"
    sleep 30s
done

# create-db-instance
cat <<EOF
aws rds create-db-instance \
    --db-instance-identifier "$DB_INSTANCE_IDENTIFIER_RESTORE" \
    --db-cluster-identifier "$DB_CLUSTER_IDENTIFIER_RESTORE" \
    --db-instance-class "$DB_INSTANCE_CLASS" \
    --engine "$ENGINE" \
    --engine-version "$ENGINE_VERSION"
EOF
CREATE_DB_INSTANCE=`aws rds create-db-instance \
    --db-instance-identifier "$DB_INSTANCE_IDENTIFIER_RESTORE" \
    --db-cluster-identifier "$DB_CLUSTER_IDENTIFIER_RESTORE" \
    --db-instance-class "$DB_INSTANCE_CLASS" \
    --engine "$ENGINE" \
    --engine-version "$ENGINE_VERSION"`
if [ $? != 0 ]; then
    date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running create-db-instance."
    exit
else
    echo $CREATE_DB_INSTANCE
fi

# polling instance status
status=""
echo "aws rds describe-db-instances --db-instance-identifier $DB_INSTANCE_IDENTIFIER_RESTORE | jq -r .DBInstances[].DBInstanceStatus"
while [ "available" != "$status" ]
do
    status=`aws rds describe-db-instances --db-instance-identifier "$DB_INSTANCE_IDENTIFIER_RESTORE" | jq -r .DBInstances[].DBInstanceStatus`
    date "+[%Y-%m-%d %H:%M:%S] $status"
    sleep 30s
done

# describe-db-instances
ENDPOINT=`aws rds describe-db-clusters --db-cluster-identifier "$DB_CLUSTER_IDENTIFIER_RESTORE" | jq -r .DBClusters[].Endpoint`

# dump
if [ "$ENGINE" = 'aurora-postgresql' ]; then
    # aurora postgresql
    export PGPASSWORD=`echo ${!SECRET_NAME} | jq -r .${PASSWORD_KEY}`
    echo "pg_dump -Fc -v -w -h ${ENDPOINT} -U ${DB_MASTER} -p ${DB_PORT} -f ${DUMP_FILE} ${DB_NAME}"
    pg_dump -Fc -v -w -h "${ENDPOINT}" -U ${DB_MASTER} -p ${DB_PORT} -f "${DUMP_FILE}" ${DB_NAME}
    if [ $? != 0 ]; then
        date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running pg_dump."
        exit
    fi
elif [ "$ENGINE" = 'aurora-mysql' ]; then
    # aurora mysql
    MYSQL_PWD=`echo ${!SECRET_NAME} | jq -r .${PASSWORD_KEY}`
    echo "mysqldump --defaults-extra-file=<(printf '[mysqldump]\npassword=%s\n' \"password\") -h ${ENDPOINT} -u ${DB_MASTER} -P ${DB_PORT} -B ${DB_NAME} --set-gtid-purged=OFF --single-transaction --verbose | gzip > ${DUMP_FILE}.gz"
    mysqldump --defaults-extra-file=<(printf '[mysqldump]\npassword=%s\n' \"${MYSQL_PWD}\") -h ${ENDPOINT} -u${DB_MASTER} -P ${DB_PORT} -B ${DB_NAME} --set-gtid-purged=OFF --single-transaction --verbose | gzip > ${DUMP_FILE}.gz
    if [ $? != 0 ]; then
        date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running mysqldump."
        exit
    fi
fi

# aws s3 cp
if [ "$ENGINE" = 'aurora-postgresql' ]; then
    # aurora postgresql
    echo "aws s3 cp $DUMP_FILE s3://${S3_BUCKET}/${S3_PREFIX}/${DB_CLUSTER_IDENTIFIER}/"
    aws s3 cp $DUMP_FILE s3://${S3_BUCKET}/${S3_PREFIX}/${DB_CLUSTER_IDENTIFIER}/
    if [ $? != 0 ]; then
        date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running aws s3 cp."
        exit
    fi
elif [ "$ENGINE" = 'aurora-mysql' ]; then
    # aurora mysql
    echo "aws s3 cp ${DUMP_FILE}.gz s3://${S3_BUCKET}/${S3_PREFIX}/${DB_CLUSTER_IDENTIFIER}/"
    aws s3 cp ${DUMP_FILE}.gz s3://${S3_BUCKET}/${S3_PREFIX}/${DB_CLUSTER_IDENTIFIER}/
    if [ $? != 0 ]; then
        date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running aws s3 cp."
        exit
    fi
fi

# delete local dump file
if [ "$ENGINE" = 'aurora-postgresql' ]; then
    # aurora postgresql
    echo "rm $DUMP_FILE"
    rm $DUMP_FILE
    if [ $? != 0 ]; then
        date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running delete local dump file."
        exit
    fi
elif [ "$ENGINE" = 'aurora-mysql' ]; then
    # aurora mysql
    echo "rm ${DUMP_FILE}.gz"
    rm ${DUMP_FILE}.gz
    if [ $? != 0 ]; then
        date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running delete local dump file."
        exit
    fi
fi

# delete-db-instance
cat <<EOF
aws rds delete-db-instance \
    --db-instance-identifier "$DB_INSTANCE_IDENTIFIER_RESTORE"
EOF
DELETE_DB_INSTANCE=`aws rds delete-db-instance \
    --db-instance-identifier "$DB_INSTANCE_IDENTIFIER_RESTORE"`

if [ $? != 0 ]; then
    date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running delete-db-instance."
    exit
else
    echo $DELETE_DB_INSTANCE
fi

# polling instance exists
echo "aws rds describe-db-instances | jq -r .DBInstances[].DBInstanceIdentifier"
while :
do
    instancelist=`aws rds describe-db-instances | jq -r .DBInstances[].DBInstanceIdentifier`
    if [ "`echo "${instancelist}" | grep -e "$DB_INSTANCE_IDENTIFIER_RESTORE"`" ]; then
        date "+[%Y-%m-%d %H:%M:%S] $DB_INSTANCE_IDENTIFIER_RESTORE exists."
        sleep 5s
    else
        date "+[%Y-%m-%d %H:%M:%S] $DB_INSTANCE_IDENTIFIER_RESTORE deleted."
        break
    fi
done

# delete-db-cluster
cat <<EOF
aws rds delete-db-cluster \
    --db-cluster-identifier "$DB_CLUSTER_IDENTIFIER_RESTORE" \
    --no-skip-final-snapshot \
    --final-db-snapshot-identifier "$DB_CLUSTER_IDENTIFIER_FINAL"
EOF
DELETE_DB_CLUSTER=`aws rds delete-db-cluster \
    --db-cluster-identifier "$DB_CLUSTER_IDENTIFIER_RESTORE" \
    --no-skip-final-snapshot \
    --final-db-snapshot-identifier "$DB_CLUSTER_IDENTIFIER_FINAL"`

if [ $? != 0 ]; then
    date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running delete-db-cluster."
    exit
else
    echo $DELETE_DB_CLUSTER
fi

# polling cluster exists
echo "aws rds describe-db-clusters | jq -r .DBClusters[].DBClusterIdentifier"
while :
do
    clusterlist=`aws rds describe-db-clusters | jq -r .DBClusters[].DBClusterIdentifier`
    if [ "`echo "${clusterlist}" | grep -e "$DB_CLUSTER_IDENTIFIER_RESTORE"`" ]; then
        date "+[%Y-%m-%d %H:%M:%S] $DB_CLUSTER_IDENTIFIER_RESTORE exists."
        sleep 5s
    else
        date "+[%Y-%m-%d %H:%M:%S] $DB_CLUSTER_IDENTIFIER_RESTORE deleted."
        break
    fi
done

# delete-db-cluster-snapshot
cat <<EOF
aws rds delete-db-cluster-snapshot \
    --db-cluster-snapshot-identifier "$DB_CLUSTER_IDENTIFIER_FINAL"
EOF
DELETE_DB_CLS_SNAPSHOT=`aws rds delete-db-cluster-snapshot \
    --db-cluster-snapshot-identifier "$DB_CLUSTER_IDENTIFIER_FINAL"`

if [ $? != 0 ]; then
    date "+[%Y-%m-%d %H:%M:%S] [ERROR] error happned when running delete-db-cluster-snapshot."
    exit
else
    echo $DELETE_DB_CLS_SNAPSHOT
fi

# end
date "+[%Y-%m-%d %H:%M:%S] all success end."
exit