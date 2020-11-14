# base image
FROM python:3.8.6-buster

# put odbc driver
COPY ./ /root/

# instal odbc
# https://www.cdata.com/jp/kb/tech/oracledb-odbc-python-linux.rst
RUN apt-get install unixODBC unixODBC-dev && \
    dpkg -i /path/to/package.deb && \
    /opt/cdata/cdata-odbc-driver-for-oracleoci/cdata.odbc.oracleoci.ini

# pip install
RUN pip3 install boto3 datetime pyodbc

# set module
COPY ./rds_logical_backup.py /root/
RUN mkdir /root/efs

# run script
CMD ["python3","/root/rds_logical_backup.py"]
