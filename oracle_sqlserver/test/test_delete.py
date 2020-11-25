import os
import datetime
import boto3
import time
from botocore.exceptions import ClientError

# rds
rds = boto3.client('rds')

# バックアップ用インスタンス削除
#try:
#    print(str(datetime.datetime.now()) + ':[info] バックアップ用インスタンス削除')
#    res = rds.delete_db_instance(
#        DBInstanceIdentifier   = "koizumi-dev-sqlserver-1st-backup",
#        SkipFinalSnapshot      = True,
#        DeleteAutomatedBackups = False
#    )
#except:
#    print(str(datetime.datetime.now()) + ':[ERROR] rds.delete_db_instance()')
#    print(res)
#    exit()

while True:
    try:
        time.sleep(3)
        res3 = rds.describe_db_instances(
            DBInstanceIdentifier   = "koizumi-dev-sqlserver-1st-backup"
        )
        print(str(datetime.datetime.now()) + ':[info] 削除中... 30s')
    except ClientError as e:
        if e.response['Error']['Code'] == 'DBInstanceNotFound':
            print(str(datetime.datetime.now()) + ':[info] バックアップ用インスタンス削除完了')
            break
            
print("end.")
