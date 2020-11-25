import backup_oracle
import backup_sqlserver
import os
import json

f = open('sample.json', 'r')
os.environ['koizumi_dev_DBPASSWORD']=f.read()

if os.environ['DB_SELECT'] == "sqlserver":
    backup_sqlserver.runsql_mss()
elif os.environ['DB_SELECT'] == "oracle":
    backup_oracle.runsql_ora()
