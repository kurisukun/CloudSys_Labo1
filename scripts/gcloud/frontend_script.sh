#!/bin/bash

git clone https://github.com/kurisukun/CloudSys_Labo1.git
cd CloudSys_Labo1/todo-app


cat << EOF > /src/constants.ts 
export const API_ENDPOINT = 'http://$__IP_BACKEND_HOST__$'
EOF

yarn && yarn build
cp -r ./dist/* /var/www/html