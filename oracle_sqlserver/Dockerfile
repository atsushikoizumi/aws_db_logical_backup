# base image
FROM python:3.8.6-buster

# [reference]
# https://dev.classmethod.jp/articles/connect-linux-to-oracle-with-odbc/
# https://qiita.com/6in/items/ac77fd4aaa77bbca9789

# put driver module
RUN  mkdir -p /root/efs/odbc
COPY ./instantclient-basic-linux.x64-19.9.0.0.0dbru.zip /root/efs/odbc/
COPY ./instantclient-odbc-linux.x64-19.9.0.0.0dbru.zip /root/efs/odbc/

# install driver etc
RUN  apt-get update -y && \
     apt-get install -y unixodbc unixodbc-dev libaio1 curl libgssapi-krb5-2

# put oracle client & odbc
RUN  mkdir -p /opt/oracle && \
     cd /root/efs/odbc/ && \
     unzip instantclient-basic-linux.x64-19.9.0.0.0dbru.zip -d /opt/oracle && \
     unzip instantclient-odbc-linux.x64-19.9.0.0.0dbru.zip -d /opt/oracle && \
     cd /opt/oracle/instantclient_19_9 && \
     sh -c "echo /opt/oracle/instantclient_19_9 > /etc/ld.so.conf.d/oracle-instantclient.conf"

# oracle odbc setting
RUN  touch /etc/odbcinst.ini; touch /etc/odbc.ini && \
     /opt/oracle/instantclient_19_9/odbc_update_ini.sh "/" /opt/oracle/instantclient_19_9 "odbcdriver19" RDSORCL /etc/odbc.ini && \
     odbcinst -i -d -f /etc/odbcinst.ini

# sqlserver odbc
RUN  curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
     curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
     apt-get update && \
     ACCEPT_EULA=Y apt-get install msodbcsql17 && \
     ACCEPT_EULA=Y apt-get install mssql-tools

# pip install
RUN  pip3 install boto3 datetime os pandas pyodbc numpy time

# set module
COPY ./test_oracle.py /root/
COPY ./test_sqlserver.py /root/

# set env
ENV  ORACLE_HOME /opt/oracle/instantclient_19_9
ENV  LD_LIBRARY_PATH $ORACLE_HOME
ENV  NLS_LANG Japanese_Japan.AL32UTF8
ENV  PATH $PATH:/opt/mssql-tools/bin

# run script
#ENTRYPOINT ["python3","/root/test_sqlserver.py"]
