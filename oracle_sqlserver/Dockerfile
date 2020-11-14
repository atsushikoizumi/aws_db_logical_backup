# base image
FROM python:3.8.6-buster

# [reference]
# https://www.cdata.com/jp/kb/tech/oracledb-odbc-python-linux.rst

# put odbc driver
RUN mkdir -p /root/efs/odbc
COPY ./OracleODBCDriverforUnix.deb /root/efs/odbc/

# install odbc driver
RUN apt-get install unixODBC unixODBC-dev && \
    dpkg -i /root/efs/odbc/package.deb
    #/opt/cdata/cdata-odbc-driver-for-oracleoci/cdata.odbc.oracleoci.ini

# pip install
RUN pip3 install boto3 datetime pyodbc

# set module
COPY ./rds_logical_backup.py /root/

# run script
CMD ["python3","/root/rds_logical_backup.py"]
