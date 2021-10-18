import openstack
import paramiko
import clean

# ------------------- Console utility constants ------------------- 
# ANSI console color codes
RED_FG      = '\u001B[31m'
YELLOW_FG   = '\u001B[33m'
GREEN_FG    = '\u001b[32m'
RESET       = '\u001B[0m'

# ------------------- Script constants  ------------------- 
# Cloud.yaml info
CLOUD_NAME              = 'openstack'
REGION_NAME             = 'ZH'

# SSH
KEY_PAIR                = 'todo-app'
SSH_PRIVATE_KEY_FILE    = 'C:\\Users\Bruno\\.ssh\\cloud-todo.key'
USERNAME                = 'ubuntu'

# SwitchEngine image name
IMG_FRONTEND            = 'Ubuntu Focal 20.04 (SWITCHengines)'
IMG_BACKEND             = 'Ubuntu Focal 20.04 (SWITCHengines)'
IMG_DB                  = 'Ubuntu Focal 20.04 (SWITCHengines)'

# Default VM flavor
FLAVOR                  = 'c1.small'

# Instances name in SwitchEngine
FRONTEND_NAME           = 'todo-frontend'
BACKEND_NAME            = 'todo-backend'
DB_NAME                 = 'todo-db'

# Public IPs
# Will be modified by the 'createFloatingIP' function
#FLOATING_IP_FRONTEND    = ''
#FLOATING_IP_BACKEND     = ''
#FLOATING_IP_DB          = ''
#PRIVATE_IP_DB           = ''

# Security group info
SEC_GROUP_NAME          = 'CloudSys-Lab1'
PORTS                   = ['3306', '80']

# ------------------- Functions ------------------- 

def create_connection_from_config():
    return openstack.connect(cloud=CLOUD_NAME, region_name=REGION_NAME)

def createFloatingIPs(conn):
    global FLOATING_IP_FRONTEND, FLOATING_IP_BACKEND, FLOATING_IP_DB
    print("{}----- Creating floating ips -----{}".format(YELLOW_FG, RESET))

    network = conn.network.find_network('public')

    FLOATING_IP_FRONTEND    = conn.network.create_ip(floating_network_id=network.id).floating_ip_address
    FLOATING_IP_BACKEND     = conn.network.create_ip(floating_network_id=network.id).floating_ip_address
    FLOATING_IP_DB          = conn.network.create_ip(floating_network_id=network.id).floating_ip_address

    print("Frontend floating ip : {}".format(FLOATING_IP_FRONTEND))
    print("Backend  floating ip : {}".format(FLOATING_IP_BACKEND))
    print("Database floating ip : {}".format(FLOATING_IP_DB))

def setupSecurityGroup(conn):
    print("{}----- Creating security group -----{}".format(YELLOW_FG, RESET))

    group = conn.network.create_security_group(name=SEC_GROUP_NAME,description="")
    print("Security group '{}' created".format(SEC_GROUP_NAME))

    for i in range(len(PORTS)):
        conn.network.create_security_group_rule(direction="ingress",protocol="tcp",port_range_max=PORTS[i],port_range_min=PORTS[i],security_group_id=group.id)
        conn.network.create_security_group_rule(direction="egress",protocol="tcp",port_range_max=PORTS[i],port_range_min=PORTS[i],security_group_id=group.id)
        print("Port {} open in '{}'".format(PORTS[i], SEC_GROUP_NAME))

    conn.network.create_security_group_rule(direction="ingress",security_group_id=group.id,remote_group_id=group.id)

    return group

def spawnFrontendInstance(conn,sec_grp):
    image = conn.compute.find_image(IMG_FRONTEND)
    flavor = conn.compute.find_flavor(FLAVOR)
    network = conn.network.find_network('private')

    print("Spawning Frontend instance...")
    server = conn.compute.create_server(
         name=FRONTEND_NAME, image_id=image.id, flavor_id=flavor.id,
         networks=[{"uuid": network.id}], key_name=KEY_PAIR)

    server = conn.compute.wait_for_server(server, status='ACTIVE')

    print("Adding instance to security groups: {}, SSH".format(SEC_GROUP_NAME))
    conn.compute.add_security_group_to_server(server, sec_grp)
    ssh_sec_grp = conn.network.find_security_group('SSH')
    conn.compute.add_security_group_to_server(server, ssh_sec_grp)
    default_sec_grp = conn.network.find_security_group('default')
    conn.compute.remove_security_group_from_server(server, default_sec_grp)

    print("Adding floating ip {} to Frontend instance".format(FLOATING_IP_FRONTEND))
    conn.compute.add_floating_ip_to_server(server, FLOATING_IP_FRONTEND, fixed_address=None)

    print("{}Frontend{} instance up and running...".format(GREEN_FG, RESET))

def spawnBackendInstance(conn,sec_grp):
    image = conn.compute.find_image(IMG_BACKEND)
    flavor = conn.compute.find_flavor(FLAVOR)
    network = conn.network.find_network('private')

    print("Spawning Backend instance...")
    server = conn.compute.create_server(
         name=BACKEND_NAME, image_id=image.id, flavor_id=flavor.id,
         networks=[{"uuid": network.id}], key_name=KEY_PAIR)

    server = conn.compute.wait_for_server(server, status='ACTIVE')

    print("Adding instance to security groups: {}, SSH".format(SEC_GROUP_NAME))
    conn.compute.add_security_group_to_server(server, sec_grp)
    ssh_sec_grp = conn.network.find_security_group('SSH')
    conn.compute.add_security_group_to_server(server, ssh_sec_grp)
    default_sec_grp = conn.network.find_security_group('default')
    conn.compute.remove_security_group_from_server(server, default_sec_grp)

    print("Adding floating ip {} to Backend instance".format(FLOATING_IP_BACKEND))
    conn.compute.add_floating_ip_to_server(server, FLOATING_IP_BACKEND, fixed_address=None)

    print("{}Backend{} instance up and running...".format(GREEN_FG, RESET))

def spawnDatabaseInstance(conn,sec_grp):
    global PRIVATE_IP_DB
    image = conn.compute.find_image(IMG_DB)
    flavor = conn.compute.find_flavor(FLAVOR)
    network = conn.network.find_network('private')

    print("Spawning Database instance...")
    server = conn.compute.create_server(
         name=DB_NAME, image_id=image.id, flavor_id=flavor.id,
         networks=[{"uuid": network.id}], key_name=KEY_PAIR)

    server = conn.compute.wait_for_server(server, status='ACTIVE')
    PRIVATE_IP_DB = server.addresses.get('private')[0].get('addr')

    print("Adding instance to security groups: {}, SSH".format(SEC_GROUP_NAME))
    conn.compute.add_security_group_to_server(server, sec_grp)
    ssh_sec_grp = conn.network.find_security_group('SSH')
    conn.compute.add_security_group_to_server(server, ssh_sec_grp)
    default_sec_grp = conn.network.find_security_group('default')
    conn.compute.remove_security_group_from_server(server, default_sec_grp)

    print("Adding floating ip {} to Database instance".format(FLOATING_IP_DB))
    conn.compute.add_floating_ip_to_server(server, FLOATING_IP_DB, fixed_address=None)

    print("{}Database{} instance up and running...".format(GREEN_FG, RESET))

def configureFrontend():
    print("{}----- Configuring Frontend -----{}".format(YELLOW_FG, RESET))

    client = paramiko.SSHClient()
    priv_key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE_KEY_FILE)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=FLOATING_IP_FRONTEND, username=USERNAME, pkey=priv_key)

    print("Updating OS...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo apt update")
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Installing Apache2...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo apt install -y apache2")
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Enabling and restarting Apache2")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo systemctl enable apache2")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo systemctl restart apache2")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -")
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Installing NodeJS...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo apt-get install -y nodejs")
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Installing Yarn...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo npm install -g yarn")
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Downloading ToDo App...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd && git clone https://github.com/kurisukun/CloudSys_Labo1.git")
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Setting the Backend ip...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd ~/CloudSys_Labo1/todo-app")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo rm -f ~/CloudSys_Labo1/todo-app/src/constants.ts")
    exit_status = ssh_stdout.channel.recv_exit_status()
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo echo \"export const API_ENDPOINT = 'http://{}:80'\" > ~/CloudSys_Labo1/todo-app/src/constants.ts".format(FLOATING_IP_BACKEND))
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Building the app...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("yarn && yarn build")
    exit_status = ssh_stdout.channel.recv_exit_status()
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo cp -r ~/CloudSys_Labo1/todo-app/dist/* /var/www/html")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo systemctl restart apache2")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    client.close

    print("{}Frontend is configured!{}".format(GREEN_FG, RESET))

def configureBackend():
    print("{}----- Configuring Backend -----{}".format(YELLOW_FG, RESET))

    client = paramiko.SSHClient()
    priv_key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE_KEY_FILE)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=FLOATING_IP_BACKEND, username=USERNAME, pkey=priv_key)

    print("Updating OS...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo apt update")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    print("Installing PHP and Apache2...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo apt install -y php php-mbstring php-xml php-dom php-zip php-intl php-mysql composer apache2")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    print("Enabling the Apache2 rewrite module...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo a2enmod rewrite")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    print("Enabling and restarting Apache2...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo systemctl enable apache2")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo systemctl restart apache2")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    print("Installing Composer...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo php -r \"copy('https://getcomposer.org/installer', 'composer-setup.php');\"")
    exit_status = ssh_stdout.channel.recv_exit_status()
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo php -r \"if (hash_file('sha384', 'composer-setup.php') === '906a84df04cea2aa72f40b5f787e49f22d4c2f19492ac310e8cba5b96ac8b64115ac402c8cd292b8a03482574915d1a8') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;\"")
    exit_status = ssh_stdout.channel.recv_exit_status()
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo php composer-setup.php")
    exit_status = ssh_stdout.channel.recv_exit_status()
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo php -r \"unlink('composer-setup.php');\"")
    exit_status = ssh_stdout.channel.recv_exit_status()
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo mv composer.phar /usr/local/bin/composer")
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Downloading and installing the API...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("git clone https://github.com/kurisukun/CloudSys_Labo1.git")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd ~/CloudSys_Labo1/todo-api")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo composer install")
    exit_status = ssh_stdout.channel.recv_exit_status()
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo mkdir /var/www/todo-api")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo cp -r ~/CloudSys_Labo1/todo-api /var/www/todo-api")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo chown -R www-data:www-data /var/www/todo-api")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo chmod -R 775 /var/www/todo-api/storage")
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Setting the virtual host up...")
    virtual_host_content =  "<VirtualHost *:80>\nServerAdmin admin@example.com\nDocumentRoot /var/www/todo-api/public\n<Directory /var/www/todo-api>\nAllowOverride All\n</Directory>\nErrorLog ${APACHE_LOG_DIR}/error.log\nCustomLog ${APACHE_LOG_DIR}/access.log combined\n</VirtualHost>\n"
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("printf '{}' | sudo tee /etc/apache2/sites-available/000-default.conf".format(virtual_host_content))
    exit_status = ssh_stdout.channel.recv_exit_status()
    

    print("Setting the database ip...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo cp /var/www/todo-api/.env.dev /var/www/todo-api/.env")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo sed -i '11s/.*/DB_HOST={}/' /var/www/todo-api/.env".format(PRIVATE_IP_DB))
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Populating database...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd /var/www/todo-api")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("php artisan migrate")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    print("Restarting the Apache2 server...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo systemctl restart apache2")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    client.close

    print("{}Backend is configured!{}".format(GREEN_FG, RESET))

def configureDatabase():
    print("{}----- Configuring Database -----{}".format(YELLOW_FG, RESET))

    client = paramiko.SSHClient()
    priv_key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE_KEY_FILE)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=FLOATING_IP_DB, username=USERNAME, pkey=priv_key)

    print("Updating OS...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo apt update")
    exit_status = ssh_stdout.channel.recv_exit_status()

    print("Installing MySQL...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo apt install -y mysql-server")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    print("Enabling and starting MySQL service...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo systemctl enable mysql")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo systemctl start mysql")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    print("Creating table and database user...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo echo \"CREATE DATABASE todo; CREATE USER 'todo'@'%' IDENTIFIED BY 'todo'; GRANT ALL PRIVILEGES ON todo.* TO 'todo'@'%'; FLUSH PRIVILEGES;\" > ./config.sql")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo mysql < ./config.sql")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    #ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("CREATE DATABASE todo;")
    #exit_status = ssh_stdout.channel.recv_exit_status() 
    #ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("CREATE USER 'todo'@'%' IDENTIFIED BY 'todo';")
    #exit_status = ssh_stdout.channel.recv_exit_status() 
    #ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("GRANT ALL PRIVILEGES ON todo.* TO 'todo'@'%';")
    #exit_status = ssh_stdout.channel.recv_exit_status() 
    #ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("FLUSH PRIVILEGES;")
    #exit_status = ssh_stdout.channel.recv_exit_status() 
    #ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("exit")
    #exit_status = ssh_stdout.channel.recv_exit_status() 

    print("Configuring listening address to 0.0.0.0...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo sed -i 's/bind-address            = 127.0.0.1/bind-address            = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf")
    exit_status = ssh_stdout.channel.recv_exit_status() 
    print("Restarting MySQL service...")
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("sudo systemctl restart mysql")
    exit_status = ssh_stdout.channel.recv_exit_status() 

    client.close()

    print("{}Database is configured!{}".format(GREEN_FG, RESET))

def main():
    conn = create_connection_from_config()

    createFloatingIPs(conn)

    sec_group = setupSecurityGroup(conn)

    print("{}----- Spawning instances -----{}".format(YELLOW_FG, RESET))
    spawnDatabaseInstance(conn, sec_group)
    spawnBackendInstance(conn, sec_group)
    spawnFrontendInstance(conn, sec_group)

    configureDatabase()
    configureBackend()
    configureFrontend()

    print("{}The ToDo App should be available at http://{}/{}".format(GREEN_FG, FLOATING_IP_FRONTEND, RESET))

if __name__ == '__main__':
    clean.main()
    main()

