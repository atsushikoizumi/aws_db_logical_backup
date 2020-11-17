import pyodbc

# 接続情報
drv = "ODBC Driver 17 for SQL Server"
edp = "koizumi-dev-sqlserver-1st.cp18wjhx9brf.eu-north-1.rds.amazonaws.com"
prt = "1433"
dbn = "xx00"
usr = "xx_adm"
pwd = "xx_adm_pass"

# 接続コマンド作成
cnxn_str = "DRIVER=%s;SERVER=%s;PORT=%s;DATABASE=%s;UID=%s;PWD=%s" % (drv,edp,prt,dbn,usr,pwd)

# 接続
cnxn = pyodbc.connect(cnxn_str)
cursor = cnxn.cursor()

sql = "SELECT @@version;"

# Sample SQL実行
cursor.execute() 
row = cursor.fetchone(sql) 
while row: 
    print(row[0])
    row = cursor.fetchone()

# 切断
cnxn.close()
