# base image
FROM python:3.8.6-buster

# [reference]
# https://www.cdata.com/jp/kb/tech/oracledb-odbc-python-linux.rst
# https://dev.classmethod.jp/articles/connect-linux-to-oracle-with-odbc/

# put driver module
RUN mkdir -p /root/efs/odbc
COPY ./OracleODBCDriverforUnix.deb /root/efs/odbc/

# install odbc driver
RUN apt install -y unixodbc unixodbc-dev && \
    dpkg -i /root/efs/odbc/OracleODBCDriverforUnix.deb

# oracle driver install
COPY ./instantclient-basic-linux.x64-19.9.0.0.0dbru.zip /root/
RUN mkdir -p /opt/oracle && \
    unzip instantclient-basic-linux.x64-19.9.0.0.0dbru.zip -d /opt/oracle && \
    apt install -y libaio1

# pip install
RUN pip3 install boto3 datetime pyodbc

# set module
COPY ./rds_logical_backup.py /root/

# run script
CMD ["python3","/root/rds_logical_backup.py"]
