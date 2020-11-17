import os
import pyodbc

# 接続情報
drv = "odbcdriver19"
dbq = "koizumi-dev-db-oracle-1st.cp18wjhx9brf.eu-north-1.rds.amazonaws.com:1521/MASTERDB"
usr = "MASTERUSER"
pwd = "Admin123!"

# 実行SQL
sql = "select USERNAME,ACCOUNT_STATUS,CREATED from dba_users order by USERNAME"

# 接続コマンド作成
coxn_str = "DRIVER=%s;DBQ=%s;UID=%s;PWD=%s" % (drv,dbq,usr,pwd)

# 接続
coxn = pyodbc.connect(coxn_str)

# カーソル取得
with coxn.cursor() as cur:
    cur.execute(sql)
    for row in cur.fetchall():
        print(row)

# 切断
coxn.close()
