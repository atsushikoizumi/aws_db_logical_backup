import os
import datetime
import boto3
import backup_oracle
import backup_sqlserver
import time
from botocore.exceptions import ClientError

# rds
rds = boto3.client('rds')

# DBインスタンス一覧取得
try:
    print(str(datetime.datetime.now()) + ':[info] DBインスタンス一覧取得')
    res1 = rds.describe_db_instances()
except:
    print(str(datetime.datetime.now()) + ':[ERROR] rds.describe_db_instances()')
    print(res1)
    exit()

# 検索条件 TagList の Env=tags_env, Owner=tags_owner
# 上記の条件で絞っておくことで他人のリソースへの影響を排除できる。
for i in range(len(res1['DBInstances'])):
    # タグ名でフィルター Env=tags_env, Owner=tags_owner なら f=2 で処理継続
    f = 0
    for j in range(len(res1['DBInstances'][i]['TagList'])):
        if str(res1['DBInstances'][i]['TagList'][j]['Key']) == 'Env':
            if  str(res1['DBInstances'][i]['TagList'][j]['Value']) == os.environ['tags_env']:
                f += 1
        if str(res1['DBInstances'][i]['TagList'][j]['Key']) == 'Owner':
            if  str(res1['DBInstances'][i]['TagList'][j]['Value']) == os.environ['tags_owner']:
                f += 1
    if f < 2:
        continue
    
    # aurora 以外なら処理継続
    if 'aurora' in str(res1['DBInstances'][i]['Engine']):
        continue

    # task で指定した DBInstanceIdentifier なら処理継続
    if os.environ['DB_INSTANCE_IDENTIFIER'] != res1['DBInstances'][i]['DBInstanceIdentifier']:
        continue

    # スナップショットの一覧を取得
    try:
        print(str(datetime.datetime.now()) + ':[info] スナップショットの一覧を取得')
        res2 = rds.describe_db_snapshots(
            DBInstanceIdentifier = os.environ['DB_INSTANCE_IDENTIFIER']
        )
    except:
        print(str(datetime.datetime.now()) + ':[ERROR] rds.describe_db_snapshots()')
        print(res2)
        exit()

    # 最新のスナップショットからリストア実行
    # rds oracle
    if "oracle" in res1['DBInstances'][i]['Engine']:
        try:
            print(str(datetime.datetime.now()) + ':[info] [oracle] 最新のスナップショットからリストア実行')
            res = rds.restore_db_instance_from_db_snapshot(
                DBInstanceIdentifier = os.environ['DB_INSTANCE_IDENTIFIER'] + "-backup",
                DBSnapshotIdentifier = res2['DBSnapshots'][-1]['DBSnapshotIdentifier'],
                DBInstanceClass      = os.environ['DB_INSTANCE_CLASS'],
                Port                 = int(os.environ['DB_PORT']),
                DBSubnetGroupName    = os.environ['DB_SUBNET_GROUP'],
                MultiAZ              = False,
                PubliclyAccessible   = False,
                AutoMinorVersionUpgrade = False,
                LicenseModel         = "license-included",
                DBName               = res1['DBInstances'][i]['DBName'],
                Engine               = res1['DBInstances'][i]['Engine'],
                DBParameterGroupName = res1['DBInstances'][i]['DBParameterGroups'][0]['DBParameterGroupName'],
                OptionGroupName      = res1['DBInstances'][i]['OptionGroupMemberships'][0]['OptionGroupName'],
                Tags                 = res1['DBInstances'][i]['TagList'],
                StorageType          = "gp2",
                VpcSecurityGroupIds  = [os.environ['VPC_SECURITY_GROUP_IDS']],
                CopyTagsToSnapshot   = True,
                EnableCloudwatchLogsExports = ["alert", "audit", "listener", "trace"],
                DeletionProtection   = False
            )
        except:
            print(str(datetime.datetime.now()) + ':[ERROR] rds.restore_db_instance_from_db_snapshot()')
            print(res)
            exit()

    # rds sqlserver
    if "sqlserver" in res1['DBInstances'][i]['Engine']:
        try:
            print(str(datetime.datetime.now()) + ':[info] [sqlserver] 最新のスナップショットからリストア実行')
            res = rds.restore_db_instance_from_db_snapshot(
                DBInstanceIdentifier = os.environ['DB_INSTANCE_IDENTIFIER'] + "-backup",
                DBSnapshotIdentifier = res2['DBSnapshots'][-1]['DBSnapshotIdentifier'],
                DBInstanceClass      = os.environ['DB_INSTANCE_CLASS'],
                Port                 = int(os.environ['DB_PORT']),
                DBSubnetGroupName    = os.environ['DB_SUBNET_GROUP'],
                MultiAZ              = False,
                PubliclyAccessible   = False,
                AutoMinorVersionUpgrade = False,
                LicenseModel         = "license-included",
                Engine               = res1['DBInstances'][i]['Engine'],
                DBParameterGroupName = res1['DBInstances'][i]['DBParameterGroups'][0]['DBParameterGroupName'],
                OptionGroupName      = res1['DBInstances'][i]['OptionGroupMemberships'][0]['OptionGroupName'],
                Tags                 = res1['DBInstances'][i]['TagList'],
                StorageType          = "gp2",
                VpcSecurityGroupIds  = [os.environ['VPC_SECURITY_GROUP_IDS']],
                CopyTagsToSnapshot   = True,
                EnableCloudwatchLogsExports = ["agent", "error"],
                DeletionProtection   = False
            )
        except:
            print(str(datetime.datetime.now()) + ':[ERROR] rds.restore_db_instance_from_db_snapshot()')
            print(res)
            exit()

    # インスタンスの状態が available になるまで待機
    try:
        print(str(datetime.datetime.now()) + ':[info] インスタンスの状態が available になるまで待機')
        waiter = rds.get_waiter('db_instance_available')
        res = waiter.wait(
            DBInstanceIdentifier = res1['DBInstances'][i]['DBInstanceIdentifier'] + "-backup"
        )
    except:
        print(str(datetime.datetime.now()) + ':[ERROR] rds.get_waiter()')
        print(res)
        exit()

    # oracle の場合、S3_INTEGRATIONのロールを付与
    if "oracle" in res1['DBInstances'][i]['Engine']:
        try:
            print(str(datetime.datetime.now()) + ':[info] [oracle] S3_INTEGRATIONのロールを付与')
            res = rds.add_role_to_db_instance(
                DBInstanceIdentifier = res1['DBInstances'][i]['DBInstanceIdentifier'] + "-backup",
                RoleArn              = os.environ['S3_INTEGRATION'],
                FeatureName          = "S3_INTEGRATION"
            )
        except:
            print(str(datetime.datetime.now()) + ':[ERROR] rds.add_role_to_db_instance()')
            print(res)
            exit()

    # バックアップ用インスタンスのENDPOINTを取得
    try:
        print(str(datetime.datetime.now()) + ':[info] バックアップ用インスタンスのENDPOINTを取得')
        res3 = rds.describe_db_instances(
            DBInstanceIdentifier = res1['DBInstances'][i]['DBInstanceIdentifier'] + "-backup"
        )
        os.environ['DB_ENDPOINT'] = res3['DBInstances'][0]['Endpoint']['Address']
    except:
        print(str(datetime.datetime.now()) + ':[ERROR] rds.describe_db_instances()')
        print(res3)
        exit()

    # 論理バックアップ開始
    if "oracle" in res1['DBInstances'][i]['Engine']:
        print(str(datetime.datetime.now()) + ':[info] [oracle] 論理バックアップ開始')
        backup_oracle.runsql_ora()
    elif "sqlserver" in res1['DBInstances'][i]['Engine']:
        print(str(datetime.datetime.now()) + ':[info] [sqlserver] 論理バックアップ開始')
        backup_sqlserver.runsql_mss()

    # バックアップ用インスタンス削除
    try:
        print(str(datetime.datetime.now()) + ':[info] バックアップ用インスタンス削除')
        res = rds.delete_db_instance(
            DBInstanceIdentifier   = res1['DBInstances'][i]['DBInstanceIdentifier'] + "-backup",
            SkipFinalSnapshot      = True,
            DeleteAutomatedBackups = False
        )
    except:
        print(str(datetime.datetime.now()) + ':[ERROR] rds.delete_db_instance()')
        print(res)
        exit()

    # バックアップ用インスタンス削除の確認
    while True:
        try:
            time.sleep(30)
            res3 = rds.describe_db_instances(
                DBInstanceIdentifier   = res1['DBInstances'][i]['DBInstanceIdentifier'] + "-backup"
            )
            print(str(datetime.datetime.now()) + ':[info] 削除中... 30s')
        except ClientError as e:
            if e.response['Error']['Code'] == 'DBInstanceNotFound':
                print(str(datetime.datetime.now()) + ':[info] バックアップ用インスタンス削除完了')
                break

    # 正常終了
    print(str(datetime.datetime.now()) + ':[info] all success end.')
