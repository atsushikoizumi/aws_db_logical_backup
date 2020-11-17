import pyodbc

# 接続情報
drv = "odbcdriver19"
dbq = "koizumi-dev-db-oracle-1st.cp18wjhx9brf.eu-north-1.rds.amazonaws.com:1521/MASTERDB"
usr = "MASTERUSER"
pwd = "Admin123!"

# 接続コマンド作成
coxn_str = "DRIVER=%s;DBQ=%s;UID=%s;PWD=%s" % (drv,dbq,usr,pwd)

# 接続
coxn = pyodbc.connect(coxn_str)

sql = "select OWNER,TABLE_NAME,TABLESPACE_NAME,CLUSTER_NAME from dba_tables where OWNER in ('XX_ADM','XY_ADM') order by OWNER,TABLE_NAME"

# カーソル取得
with coxn.cursor() as cur:
    cur.execute(sql)
    for row in cur.fetchall():
        print(row)

# 切断
coxn.close()

hoge = {'EXP_MODE': "", 'EXP_DUMP_NAME': "", 'EXP_LOG_NAME': "", 'EXP_DIR': "", 'SCHEMA_NAME': ""}

hoge['EXP_MODE'] = "SCHEMA"
hoge['EXP_DUMP_NAME'] = "sample.dmp"
hoge['EXP_LOG_NAME'] = "oracke_dump.log"
hoge['EXP_DIR'] = "DATA_PUMP_DIR"
hoge['SCHEMA_NAME'] = "XX_ADM"

# 実行SQL
sql = '''DECLARE
hdnl NUMBER;
status VARCHAR2(20);
BEGIN
    hdnl := DBMS_DATAPUMP.open( operation => 'EXPORT', job_mode => '{EXP_MODE}', job_name=>null);
    DBMS_DATAPUMP.ADD_FILE( handle => hdnl, filename => '{EXP_DUMP_NAME}', directory => '{EXP_DIR}',
                    filetype => dbms_datapump.ku$_file_type_dump_file, reusefile => 1 );
    DBMS_DATAPUMP.ADD_FILE( handle => hdnl, filename => '{EXP_LOG_NAME}', directory => '{EXP_DIR}',
                filetype => dbms_datapump.ku$_file_type_log_file, reusefile => 1);
    DBMS_DATAPUMP.METADATA_FILTER(hdnl,'SCHEMA_EXPR','IN '{SCHEMA_NAME}');
    DBMS_DATAPUMP.START_JOB(handle => hdnl);
    DBMS_DATAPUMP.WAIT_FOR_JOB(hdnl,status);
END;
/'''.format(**hoge)

print(sql)
