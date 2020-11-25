import os
import pyodbc
import time
import pandas as pd
import numpy as np
import datetime

#
# pyodbcはプロシージャの結果を返さない。
# oracleの場合は、おそらくcx_Oracleを使うべき。
#

def runsql_ora():

    # 接続情報
    drv = "odbcdriver19"
    dbq = os.environ['DB_ENDPOINT'] + ":" + os.environ['DB_PORT'] + "/" + os.environ['DB_NAME']
    usr = os.environ['DB_MASTER']
    pwd = os.environ['DB_PASSWORD']

    # バックアップ環境変数
    os.environ["NLS_LANG"] = "JAPANESE_JAPAN.AL32UTF8"
    hoge = {'EXP_P_PREFIX': "", 'EXP_MODE': "", 'EXP_DUMP_NAME': "", 'EXP_LOG_NAME': "", 'EXP_DIR': "", 'SCHEMA_NAME': "", 'S3_BUCKET': "", 'S3_PREFIX': ""}
    hoge['EXP_P_PREFIX'] = os.environ['DB_INSTANCE_IDENTIFIER'] + "-"
    hoge['EXP_MODE'] = "SCHEMA"
    hoge['EXP_DUMP_NAME'] = os.environ['DB_INSTANCE_IDENTIFIER'] + "-" + os.environ['DB_SCHEMA'] + ".dmp"
    hoge['EXP_LOG_NAME'] = os.environ['DB_INSTANCE_IDENTIFIER'] + "-" + os.environ['DB_SCHEMA'] +  ".log"
    hoge['EXP_DIR'] = "DATA_PUMP_DIR"
    hoge['SCHEMA_NAME'] = os.environ['DB_SCHEMA']
    hoge['S3_BUCKET'] = os.environ['S3_BUCKET']
    ymd = datetime.date.today().strftime('%Y%m%d')
    hoge['S3_PREFIX'] = os.environ['S3_PREFIX'] + "/" + os.environ['DB_INSTANCE_IDENTIFIER'] + "/" + ymd + "/" 

    # 接続コマンド作成
    con_str = "DRIVER=%s;DBQ=%s;UID=%s;PWD=%s" % (drv,dbq,usr,pwd)

    # 接続
    try:
        con = pyodbc.connect(con_str)
        con.setencoding('utf-8')
    except:
        print(con)
        exit()

    # カーソル作成
    cur = con.cursor()

    # 01. バックアップ開始
    sql = '''
        DECLARE
        hdnl NUMBER;
        status VARCHAR2(20);
        job_state VARCHAR2(30);
        js VARCHAR2(256);
        sts ku$_Status1010;
        BEGIN
            hdnl := DBMS_DATAPUMP.open( operation => 'EXPORT',
                                        job_mode  => '{EXP_MODE}',
                                        job_name  => null );
            DBMS_DATAPUMP.ADD_FILE( handle    => hdnl,
                                    filename  => '{EXP_DUMP_NAME}',
                                    directory => '{EXP_DIR}',
                                    filetype  => dbms_datapump.ku$_file_type_dump_file,
                                    reusefile => 1 );
            DBMS_DATAPUMP.ADD_FILE( handle    => hdnl,
                                    filename  => '{EXP_LOG_NAME}',
                                    directory => '{EXP_DIR}',
                                    filetype  => dbms_datapump.ku$_file_type_log_file,
                                    reusefile => 1 );
            DBMS_DATAPUMP.METADATA_FILTER( hdnl,
                                        'SCHEMA_LIST',
                                        ' ''{SCHEMA_NAME}'' ');
            DBMS_DATAPUMP.START_JOB( handle => hdnl );
            DBMS_DATAPUMP.WAIT_FOR_JOB( hdnl,status );
        END;
        '''.format(**hoge)
    try:
        row = cur.execute(sql)
    except:
        print(sql)
        print(row.fetchall())
        exit()

    # 02. バックアップの結果確認
    sql = '''
        SELECT TEXT FROM TABLE(RDSADMIN.RDS_FILE_UTIL.READ_TEXT_FILE('{EXP_DIR}','{EXP_LOG_NAME}'));
        '''.format(**hoge)
    try:
        row = cur.execute(sql)
    except:
        print(sql)
        print(row.fetchall())
        exit()
    df = pd.DataFrame(np.array(row.fetchall()))
    if '正常に完了しました' in df.iloc[-1,0]:
        print(df.iloc[-1,0])
    else:
        print(df.iloc[-1,0])
        print("[ERROR] 異常終了")
        exit()

    # 03
    sql03 = '''
        SELECT rdsadmin.rdsadmin_s3_tasks.upload_to_s3 (
            p_bucket_name    =>  '{S3_BUCKET}',
            p_s3_prefix      =>  '{S3_PREFIX}',
            p_directory_name =>  '{EXP_DIR}',
            p_prefix         =>  '{EXP_P_PREFIX}')
        FROM DUAL;
        '''.format(**hoge)
    print(sql03)
    try:
        # 原因不明でよくコケる。少しの間 sleep させる。
        time.sleep(30)
        row = cur.execute(sql03)
        task_id_log = "dbtask-" + row.fetchall()[0][0] + ".log"
    except:
        print(sql03)
        print(row.fetchall())
        exit()

    # 04
    start = time.time()
    while True:

        sql04 = '''
            SELECT text FROM table(rdsadmin.rds_file_util.read_text_file('BDUMP','{}'));
            '''.format(task_id_log)

        t = time.time() - start
        if t > 300:
            print("[ERROR] 30分異常経過のため以上終了")
            exit()
        time.sleep(10)

        try:
            res = ""
            res = cur.execute(sql04).fetchall()
        except:
            continue

        for i in res:
            print(i[0])
            if "The task finished successfully." in i[0]:
                print("s3 upload successfully.")
                # この break は for に対してのみ有効である。
                break
            # タスク失敗時、upload_to_s3 をリトライさせる。
            elif "The task failed." in i[0]:
                try:
                    row = cur.execute(sql03)
                    task_id_log = "dbtask-" + row.fetchall()[0][0] + ".log"
                except:
                    print(sql03)
                    print(row.fetchall())
                    exit()
        else:
            # if 内で break しなければ continue する。
            print("s3 uploading.")
            continue
        
        # if 内で break したら外側の while も break する。
        break

    # 切断
    con.close()
