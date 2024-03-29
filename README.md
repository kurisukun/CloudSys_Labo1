# CloudSys_Labo1

## IaaS attribution


Gil : AWS Amazon

Chris : GCE

Arthur : Azure

Bruno : SwitchEngine

Laurent: Exoscale

## Installation de l'application

### Base de données

- Installer MySQL
- Créer une base de donnée appelée `todo` avec un user `todo` et un mot de passe
```mysql
CREATE DATABASE todo;
CREATE USER 'todo'@'%' IDENTIFIED BY 'todo';
GRANT ALL PRIVILEGES ON todo.* TO 'todo'@'%';
FLUSH PRIVILEGES;
```
- Configurer le serveur pour écouter sur 0.0.0.0 au lieu de localhost (https://linuxize.com/post/mysql-remote-access/)
- Créer un *security group*
- Ouvrir le port 3306 du noeud vers l'extérieur
- Save the instance as an image for later deployments

### Backend API

- Choisir une image Ubuntu 20.04
- Installer PHP et Apache2

```shell
# Apache2 is automatically installed with the php package
sudo apt update && \
sudo apt install php php-mbstring php-xml php-dom php-zip php-intl php-mysql composer
```
- Enable the rewrite module for Apache2
```shell
sudo a2enmod rewrite && sudo systemctl restart apache2
```
- Clone the code
```shell
git clone https://github.com/kurisukun/CloudSys_Labo1.git
cd CloudSys_Labo1/todo-api
composer install
sudo mkdir /var/www/todo-api
sudo cp -r . /var/www/todo-api
sudo chown -R www-data:www-data /var/www/todo-api
sudo chmod -R 775 /var/www/todo-api/storage
```
- Update the Apache2 default config (`/etc/apache2/sites-available/000-default.conf`)
```
<VirtualHost *:80>
    ServerAdmin admin@example.com
    DocumentRoot /var/www/todo-api/public
    <Directory /var/www/todo-api>
        AllowOverride All
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
- Update the Laravel configuration
```
cd /var/www/todo-api
sudo cp .env.dev .env
```
- Update the database connection (`.env` file) with the IP of the database node and credentials
```
DB_CONNECTION=mysql
DB_HOST=<ip of node>
DB_PORT=3306
DB_DATABASE=todo
DB_USERNAME=todo
DB_PASSWORD=<choosen password>
```
- Run migration to populate the database
```shell
cd /var/www/todo-api
php artisan migrate
```
- Create security group and open port 80
- Save the instance as an image for later deployments

### Frontend app

- Install Apache2
```shell
sudo apt update
sudo apt install apache2
```
- Install NodeJS and Yarn
```shell
curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g yarn
```
- Clone the code
```shell
git clone https://github.com/kurisukun/CloudSys_Labo1.git
cd CloudSys_Labo1/todo-app
```
- Update the API_ENDPOINT (`todo-app/src/constants.ts`) with the laravel node IP address
- Build the app
```shell
yarn && yarn build
```
- Deploy the static app
```shell
sudo cp -r ./dist/* /var/www/html
```
- Create a security group with port 80 open
- Save the instance as an image for later deployments
