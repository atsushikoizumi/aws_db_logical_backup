# base image
FROM python:3.8.6-buster

# [reference]
# https://www.cdata.com/jp/kb/tech/oracledb-odbc-python-linux.rst
# https://dev.classmethod.jp/articles/connect-linux-to-oracle-with-odbc/

# put driver module
RUN mkdir -p /root/efs/odbc
COPY ./OracleODBCDriverforUnix.deb /root/efs/odbc/

# install odbc driver 
RUN apt-get update -y && \
    apt-get install -y unixodbc unixodbc-dev
#    dpkg -i /root/efs/odbc/OracleODBCDriverforUnix.deb

# put oracle client
COPY ./instantclient-basic-linux.x64-19.9.0.0.0dbru.zip /root/efs/odbc/
RUN mkdir -p /opt/oracle && \
    cd /root/efs/odbc/ && \
    unzip instantclient-basic-linux.x64-19.9.0.0.0dbru.zip -d /opt/oracle && \
    cd /opt/oracle/instantclient_19_9 && \
    sh -c "echo /opt/oracle/instantclient_19_9 > /etc/ld.so.conf.d/oracle-instantclient.conf" && \
    mkdir -p /opt/oracle/instantclient_19_9/network/admin && \
    apt-get install -y libaio1

# pip install
RUN pip3 install boto3 datetime pyodbc

# set module
#COPY ./rds_logical_backup.py /root/

# run script
#CMD ["python3","/root/rds_logical_backup.py"]
