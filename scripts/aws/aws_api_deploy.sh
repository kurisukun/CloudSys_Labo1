#!/bin/bash
export HOME=/root
yum update -y
amazon-linux-extras enable php7.4
yum clean metadata
yum install -y git php php-{cli,mbstring,gd,mysqlnd,xml,intl,zip}
php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
php -r "if (hash_file('sha384', 'composer-setup.php') === '906a84df04cea2aa72f40b5f787e49f22d4c2f19492ac310e8cba5b96ac8b64115ac402c8cd292b8a03482574915d1a8') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"
php composer-setup.php
php -r "unlink('composer-setup.php');"
mv composer.phar /usr/bin/composer
cat << EOF > /etc/httpd/conf.d/zzz-api.conf
<VirtualHost *:80>
    ServerAdmin admin@example.com
    DocumentRoot /var/www/todo-api/public
    <Directory /var/www/todo-api>
        AllowOverride All
    </Directory>
</VirtualHost>
EOF
git clone https://github.com/kurisukun/CloudSys_Labo1.git
mv CloudSys_Labo1/todo-api /var/www/todo-api
cd /var/www/todo-api
composer install
sudo chown -R apache:apache .
sudo chmod -R 775 ./storage
cp .env.prod .env
cat << EOF >> .env
DB_CONNECTION=mysql
DB_HOST=$$$db_node_ip$$$
DB_PORT=3306
DB_DATABASE=todo
DB_USERNAME=todo
DB_PASSWORD=todo
EOF
php artisan migrate --force
systemctl enable --now httpd