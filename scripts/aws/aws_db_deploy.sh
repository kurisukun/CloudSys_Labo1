#!/bin/bash
yum update -y
yum install -y mariadb-server
cat << EOF > /etc/my.cnf
[mysqld]
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
symbolic-links=0
bind-address=0.0.0.0

[mysqld_safe]
log-error=/var/log/mariadb/mariadb.log
pid-file=/var/run/mariadb/mariadb.pid

!includedir /etc/my.cnf.d
EOF
systemctl enable --now mariadb
mysql -e "CREATE DATABASE todo"
mysql -e "CREATE USER 'todo'@'%' IDENTIFIED BY 'todo'"
mysql -e "GRANT ALL PRIVILEGES ON todo.* TO 'todo'@'%'"
mysql -e "FLUSH PRIVILEGES"