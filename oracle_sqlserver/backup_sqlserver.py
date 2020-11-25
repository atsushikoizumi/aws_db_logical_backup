import os
import pyodbc
import time
import datetime
import json

def runsql_mss():

    # 接続情報
    drv = "ODBC Driver 17 for SQL Server"
    edp = os.environ['DB_ENDPOINT']
    prt = os.environ['DB_PORT']
    dbn = os.environ['DB_NAME']
    usr = os.environ['DB_MASTER']
    se_nm = os.environ['tags_owner'] + "_" + os.environ['tags_env'] + "_DBPASSWORD"
    ps = json.loads(os.environ["{}".format(se_nm)])
    pwd = ps[os.environ['PASSWORD_KEY']]

    # バックアップ環境変数
    hoge = {'DB_INSTANCE_IDENTIFIER': "", 'DB_NAME': "", 'BACKUP_FILE': "", 'S3_BUCKET': "", 'S3_PREFIX': ""}
    hoge['DB_INSTANCE_IDENTIFIER'] = os.environ['DB_INSTANCE_IDENTIFIER']
    hoge['DB_NAME'] = os.environ['DB_NAME']
    hoge['BACKUP_FILE'] = os.environ['DB_INSTANCE_IDENTIFIER'] + "-" + os.environ['DB_NAME'] + ".bak"
    hoge['S3_BUCKET'] = os.environ['S3_BUCKET']
    ymd = datetime.date.today().strftime('%Y%m%d')
    hoge['S3_PREFIX'] = os.environ['S3_PREFIX'] + "/" + os.environ['DB_INSTANCE_IDENTIFIER'] + "/" + ymd

    # 接続コマンド作成
    con_str = "DRIVER=%s;SERVER=%s;PORT=%s;DATABASE=%s;UID=%s;PWD=%s" % (drv,edp,prt,dbn,usr,pwd)

    # 接続
    con = pyodbc.connect(con_str)
    con.setencoding('utf-8')

    # カーソル作成
    cur = con.cursor()

    # 01
    sql = '''
        exec rdsadmin..rds_show_configuration 'S3 backup compression'
        '''
    print(cur.execute(sql).fetchall())

    # 02
    sql = '''
        exec rdsadmin..rds_set_configuration 'S3 backup compression', 'true'
        commit
        '''
    cur.execute(sql)

    # 03
    sql = '''
        exec rdsadmin..rds_show_configuration 'S3 backup compression'
        '''
    print(cur.execute(sql).fetchall())


    # 04
    sql = '''
        exec msdb.dbo.rds_backup_database 
        @source_db_name='{DB_NAME}', 
        @s3_arn_to_backup_to='arn:aws:s3:::{S3_BUCKET}/{S3_PREFIX}/{BACKUP_FILE}',
        @overwrite_s3_backup_file=1,
        @number_of_files=1,
        @type='FULL';
        commit
        '''.format(**hoge)
    try:
        row = cur.execute(sql)
    except:
        print(sql)
        print(row)
        exit()

    # 05
    sql = '''
        exec msdb.dbo.rds_task_status @db_name='{DB_NAME}';
        commit
        '''.format(**hoge)
    task_status = ""
    while task_status != "SUCCESS":
        try:
            row = cur.execute(sql)
        except:
            print(sql)
            print(row)
            exit()
        res = row.fetchall()[0]
        task_status = res[5]
        if task_status == "ERROR":
            print(res[6])
            exit()
        else:
            time.sleep(30)
            print(task_status)

    # 06
    sql = '''
        exec rdsadmin..rds_set_configuration 'S3 backup compression', 'false'
        commit
        '''
    cur.execute(sql)

    # 07
    sql = '''
        exec rdsadmin..rds_show_configuration 'S3 backup compression'
        '''
    print(cur.execute(sql).fetchall())

    # 切断
    con.close()
