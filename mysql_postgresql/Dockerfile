# ベースイメージ
FROM amazonlinux:2

# 初期設定
RUN yum -y update && \
    # 追加で必要なパッケージをインストール
    rpm -ivh --nodeps https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm && \
    sed -i "s/\$releasever/7/g" "/etc/yum.repos.d/pgdg-redhat-all.repo" && \
    yum -y install awscli jq postgresql12 && \
    # mysqldump 5.7 をインストール
    yum install -y https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm && \
    yum install -y yum-utils && \
    yum-config-manager --disable mysql80-community && \
    yum-config-manager --enable mysql57-community && \
    yum install -y mysql-community-client && \
    # キャッシュを削除
    yum clean all && \
    # JST
    touch /etc/sysconfig/clock && \
    echo 'ZONE="Asia/Tokyo"' >> /etc/sysconfig/clock&& \
    echo 'UTC=false' >> /etc/sysconfig/clock && \
    ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    # locale
    touch /etc/sysconfig/i18n && \
    echo 'ja_JP.UTF-8' >> /etc/sysconfig/i18n

COPY ./rds_logical_backup.sh /root/
RUN chmod 755 /root/rds_logical_backup.sh
RUN mkdir /root/efs
ENTRYPOINT ["/root/rds_logical_backup.sh"]
