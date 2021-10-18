import exoscale

# ===== Variables ===== 

frontend_image_id = '4d9d585a-ccb9-4f24-a5e5-736bbc8ec333'
backend_image_id = 'c06cfc83-9f33-42fe-80fa-29f9ec0e7870'
mysql_image_id = '31843cd6-8c4f-4605-a0f3-bdaacc97bcb1'

frontend_ip = '192.168.1.120/24'
backend_ip = '192.168.1.100/24'
mysql_ip = '192.168.1.40/24'

# Credentials are hard-coded -> Why ? 
# That's in order to allow you to access my templates easily, and to deploy them image-based
# This is obviously not a good practice, and in a real case scenario the person running the script would have environ variables configured
# To be indentified as a member of the organisation, allowed to access the templates

# Run the following two lines in your terminal if not set
# export EXOSCALE_API_KEY=EXOfc6647dfb8755a57e2624fb4
# export EXOSCALE_API_SECRET=yAC5JA4GgrqcU4WzT3cXuWtxCv4vMS603jCPBG4g-CY

# More elegant solution uses subprocess for the export but it's a bit intrusive

# ===== Default configs =====

# Initiate our exoscale object
exo = exoscale.Exoscale()

# Retrieve the computing zone GVA-2 that we plan to work with
zone_gva2 = exo.compute.get_zone("ch-gva-2")

# Create a private network for our VMs
network = exo.compute.create_private_network(zone_gva2, "todo-network")

# Create a security group for our instances, his name will be "todo"
security_group_web = exo.compute.create_security_group("todo_web_apps")
security_group_sql = exo.compute.create_security_group("todo_mysql")

# Add default rules to our security group, saying we want to allow HTTP/HTTPS access
for rule in [
    exoscale.api.compute.SecurityGroupRule.ingress(
        description="HTTP",
        network_cidr="0.0.0.0/0",
        port="80",
        protocol="tcp",
    ),
    exoscale.api.compute.SecurityGroupRule.ingress(
        description="HTTPS",
        network_cidr="0.0.0.0/0",
        port="443",
        protocol="tcp",
    ),
    exoscale.api.compute.SecurityGroupRule.ingress(
        description="SSH",
        network_cidr="0.0.0.0/0",
        port="22",
        protocol="tcp",
    ),
]: 
    security_group_web.add_rule(rule)

# Add default rules to our security group, saying we want to allow HTTP/HTTPS access
for rule in [
    exoscale.api.compute.SecurityGroupRule.ingress(
        description="MySQL",
        network_cidr="0.0.0.0/0",
        port="3306",
        protocol="tcp",
    ),
    exoscale.api.compute.SecurityGroupRule.ingress(
        description="SSH",
        network_cidr="0.0.0.0/0",
        port="22",
        protocol="tcp",
    ),
]: 
    security_group_sql.add_rule(rule)

# Create an elastic IP address
elastic_ip = exo.compute.create_elastic_ip(zone_gva2)

# ===== Cloud config / user data stuff =====

# Mostly tells the instance to upgrade it's package, and verfy that the service is running
# Based on https://cloudinit.readthedocs.io/en/latest/topics/network-config.html and many other stackoverflows
# We need to use an integrated command to change the network, in our case (Ubuntu) it's netplan

user_data_template = """ 
#cloud-config
package_upgrade: true
write_files:
  - path: /etc/netplan/config.yaml
    content: |
      network:
        version: 2
        ethernets:
          eth0:
            adresses:
              - {ip_address}
runcmd:
  - netplan generate
  - netplan apply
"""

frontend_user_data = user_data_template.format(ip_address=frontend_ip)
backend_user_data = user_data_template.format(ip_address=backend_ip)
mysql_user_data = user_data_template.format(ip_address=mysql_ip)


# ===== Create the instances =====

frontend = exo.compute.create_instance(
    name="todo-frontend",
    zone=zone_gva2,
    type=exo.compute.get_instance_type("medium"),
    template=exo.compute.get_instance_template(zone_gva2, frontend_image_id),
    volume_size=50,
    security_groups=[security_group_web],
    private_networks=[network],
    user_data=frontend_user_data
)

backend = exo.compute.create_instance(
    name="todo-backend",
    zone=zone_gva2,
    type=exo.compute.get_instance_type("medium"),
    template=exo.compute.get_instance_template(zone_gva2, backend_image_id),
    volume_size=50,
    security_groups=[security_group_web],
    private_networks=[network],
    user_data=backend_user_data
)

database = exo.compute.create_instance(
    name="todo-mysql",
    zone=zone_gva2,
    type=exo.compute.get_instance_type("small"),
    template=exo.compute.get_instance_template(zone_gva2, mysql_image_id),
    volume_size=50,
    security_groups=[security_group_web],
    private_networks=[network],
    user_data=mysql_user_data
)


# Attach our elasctic IP address to the frontend instance
frontend.attach_elastic_ip(elastic_ip)


# ===== Verify the results =====

# Print the details of every instances
for instance in exo.compute.list_instances():
    print("{name} {zone} {ip}".format(
        name=instance.name,
        zone=instance.zone.name,
        ip=instance.ipv4_address,
    ))
