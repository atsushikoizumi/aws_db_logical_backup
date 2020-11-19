import os
import pyodbc
import pandas as pd
import numpy as np
import datetime

#
# pyodbcはプロシージャの結果を返さない。
# oracleの場合は、おそらくcx_Oracleを使うべき。
#

def runsql_ora():

    # 接続情報
    drv = "ORACLEODBCDRIVER"
    dbq = os.environ['DB_ENDPOINT'] + ":" + os.environ['DB_PORT'] + "/" + os.environ['DB_NAME']
    usr = os.environ['DB_MASTER']
    pwd = os.environ['DB_PASSWORD']

    # バックアップ環境変数
    os.environ["NLS_LANG"] = "JAPANESE_JAPAN.AL32UTF8"
    hoge = {'EXP_MODE': "", 'EXP_DUMP_NAME': "", 'EXP_LOG_NAME': "", 'EXP_DIR': "", 'SCHEMA_NAME': "", 'S3_BUCKET': "", 'S3_PREFIX': ""}
    hoge['EXP_MODE'] = "SCHEMA"
    hoge['EXP_DUMP_NAME'] = os.environ['DB_INSTANCE_IDENTIFIER'] + "-" + os.environ['DB_SCHEMA'] + ".dmp"
    hoge['EXP_LOG_NAME'] = "oracle_dump.log"
    hoge['EXP_DIR'] = "DATA_PUMP_DIR"
    hoge['SCHEMA_NAME'] = os.environ['DB_SCHEMA']
    hoge['S3_BUCKET'] = os.environ['S3_BUCKET']
    ymd = datetime.date.today().strftime('%Y%m%d')
    hoge['S3_PREFIX'] = os.environ['S3_PREFIX'] + "/" + os.environ['DB_INSTANCE_IDENTIFIER'] + "/" + ymd + "/" 

    # 接続コマンド作成
    con_str = "DRIVER=%s;DBQ=%s;UID=%s;PWD=%s" % (drv,dbq,usr,pwd)

    # 接続
    con = pyodbc.connect(con_str)
    con.setencoding('utf-8')

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
        print(row)
        exit()

    # 02. バックアップの結果確認
    sql = '''
        SELECT TEXT FROM TABLE(RDSADMIN.RDS_FILE_UTIL.READ_TEXT_FILE('{EXP_DIR}','{EXP_LOG_NAME}'))
        '''.format(**hoge)
    try:
        row = cur.execute(sql)
    except:
        print(sql)
        print(row)
        exit()
    df = pd.DataFrame(np.array(row.fetchall()))
    if '正常に完了しました' in df.iloc[-1,0]:
        print(df.iloc[-1,0])
    else:
        print(df.iloc[-1,0])
        print("[ERROR] 異常終了")
        exit()

    # 03
    sql = '''
        SELECT rdsadmin.rdsadmin_s3_tasks.upload_to_s3 (
            p_bucket_name    =>  '{S3_BUCKET}',
            p_s3_prefix      =>  '{S3_PREFIX}',
            p_directory_name =>  '{EXP_DIR}')
        AS task_id FROM DUAL;
        '''.format(**hoge)
    try:
        row = cur.execute(sql)
    except:
        print(sql)
        print(row)
        exit()

    # 切断
    con.close()
