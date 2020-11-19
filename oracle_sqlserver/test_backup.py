import backup_oracle
import backup_sqlserver
import os

if os.environ['DB_SELECT'] == "sqlserver":
    backup_sqlserver.runsql_mss()
elif os.environ['DB_SELECT'] == "oracle":
    backup_oracle.runsql_ora()
