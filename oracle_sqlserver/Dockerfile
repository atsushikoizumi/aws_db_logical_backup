# ベースイメージ
FROM python:3.8.6-buster

# pip install
RUN pip3 install boto3 datetime

# set module
COPY ./rds_logical_backup.py /root/
RUN mkdir /root/efs

# run script
ENTRYPOINT ["python3","/root/rds_logical_backup.py"]
