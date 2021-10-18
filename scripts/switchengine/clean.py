import openstack

# ------------------- Console utility constants ------------------- 
# ANSI console color codes
RED_FG      = '\u001B[31m'
RESET       = '\u001B[0m'

# ------------------- Script constants  ------------------- 
# Cloud.yaml info
CLOUD_NAME              = 'openstack'
REGION_NAME             = 'ZH'

# Security group info
SEC_GROUP_NAME          = 'CloudSys-Lab1'

# ------------------- Functions ------------------- 

def create_connection_from_config():
    return openstack.connect(cloud=CLOUD_NAME, region_name=REGION_NAME)

def deleteInstances(conn):
    servers = conn.compute.servers(details=False)
    for instance in servers:
        print("Deleting instance: {}{}{}...".format(RED_FG, instance.name, RESET))
        conn.compute.delete_server(instance.id)
        #server = conn.compute.wait_for_server(instance, status='DELETED')

def deleteFloatingIPs(conn):
    floating_ips = conn.network.ips()
    for ip in floating_ips:
        print("Deleting floating ip: {}{}{}...".format(RED_FG, ip.id, RESET))
        conn.network.delete_ip(ip.id)

def deleteSecurityGroup(conn):
    sec_grp = conn.network.find_security_group(SEC_GROUP_NAME)
    print("Deleting security group: {}{}{}".format(RED_FG, sec_grp.name, RESET))
    conn.network.delete_security_group(sec_grp.id)

def deleteVolumes(conn):
    volumes = conn.block_storage.volumes()
    for volume in volumes:
        if volume.attachments:
            print("Deleting volume: {}{}{}...".format(RED_FG, volume.name, RESET))
            conn.block_storage.delete_volume(volume.id)

def main():
    print("{}----- Cleaning cloud -----{}".format(RED_FG, RESET))
    conn = create_connection_from_config()
    deleteInstances(conn)
    deleteVolumes(conn)
    deleteFloatingIPs(conn)
    deleteSecurityGroup(conn)
    
    
if __name__ == '__main__':
    main()