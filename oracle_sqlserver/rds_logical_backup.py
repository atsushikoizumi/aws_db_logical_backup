import os
import datetime
import boto3

# rds
rds = boto3.client('rds')

# describe_db_instances
try:
    res1 = rds.describe_db_instances()
except:
    print(str(datetime.datetime.now()) + ':[ERROR] rds.describe_db_instances()')
    exit()

# DBInstanceIdentifier を動的に取得
# 検索条件1 TagList の Env=tags_env, Owner=tags_owner
# 検索条件2 Engine に aurora が含まれない。
# 上記の条件で絞っておくことで他人のリソースを指定できない。
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

    # スナップショットの一覧を配列で取得
    try:
        res2     = rds.describe_db_snapshots()
        res2_ary = []
    except:
        print(str(datetime.datetime.now()) + ':[ERROR] rds.describe_db_snapshots()')
        exit()

    # task で指定した DBInstanceIdentifier なら処理継続
    if os.environ['DB_INSTANCE_IDENTIFIER'] != res1['DBInstances'][i]['DBInstanceIdentifier']:
        continue

    # 最新のスナップショット名を取得
    res2_ary.sort(reverse=True)

    print(res1['DBInstances'][i]['Endpoint']['Address'])
    print(res1['DBInstances'][i]['Endpoint']['Port'])

    # restore_db_instance_from_db_snapshot
    # rds oracle
    if "oracle" in res1['DBInstances'][i]['Engine']:
        try:
            rds.restore_db_instance_from_db_snapshot(
                DBInstanceIdentifier = os.environ['DB_INSTANCE_IDENTIFIER'] + "-backup",
                DBSnapshotIdentifier = res2_ary[0],
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
                VpcSecurityGroupIds  = [
                    os.environ['VPC_SECURITY_GROUP_IDS'],
                ],
                CopyTagsToSnapshot   = True,
                EnableCloudwatchLogsExports = [
                    "alert", "audit", "listener", "trace"
                ],
                DeletionProtection   = False
            )
        except:
            print(str(datetime.datetime.now()) + ':[ERROR] rds.restore_db_instance_from_db_snapshot()')
            exit()

    # waite instance available
    try:
        waiter = rds.get_waiter('db_instance_available')
        waiter.wait(
            DBInstanceIdentifier = res1['DBInstances'][i]['DBInstanceIdentifier'] + "-backup"
        )
    except:
        print(str(datetime.datetime.now()) + ':[ERROR] rds.get_waiter()')
        exit()

    # logical backup
    
    cnxn = pyodbc.connect('DRIVER={CData ODBC Driver for Oracle};User=masteruser;Password="ADmin123!";Server=koizumi-dev-db-oracle-1st.cp18wjhx9brf.eu-north-1.rds.amazonaws.com;Port=1521;')

    #delete_db_snapshot
