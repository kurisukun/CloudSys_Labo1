#!/bin/bash
yum update -y
yum install -y git httpd
export HOME=/root
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. $HOME/.nvm/nvm.sh
nvm install node
npm install -g yarn
git clone https://github.com/kurisukun/CloudSys_Labo1.git
cd CloudSys_Labo1/todo-app
cat << EOF > src/constants.ts
export const API_ENDPOINT = 'http://$$$api_node_ip$$$'
EOF
yarn
yarn build
cp -r ./dist/* /var/www/html
chown -R apache:apache /var/www/html
systemctl enable --now httpd