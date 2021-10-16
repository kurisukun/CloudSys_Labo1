#!/bin/bash
cd /var/www/todo-api

cat << EOF >> .env 
DB_HOST=$__IP_DB_HOST__$
DB_PORT=3306
DB_DATABASE=todo
DB_USERNAME=todo
DB_PASSWORD=todo1234
EOF