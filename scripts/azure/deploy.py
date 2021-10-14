from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient


# Definitions for ip, nic, and vm provisions
def provision_ip(rg_name, vm_name, location):
    return network_client.public_ip_addresses.begin_create_or_update(
        rg_name,
        vm_name + '-ip',
        {
            "location": location,
            "sku": {"name": "Basic"},
            "public_ip_allocation_method": "Dynamic",
            "public_ip_address_version": "IPV4"
        }
    ).result()


def provision_nic(rg_name, vm_name, location, subnet_id, ip_id, nsg_id):
    return network_client.network_interfaces.begin_create_or_update(
        rg_name,
        vm_name + '-nic',
        {
            "location": location,
            "ip_configurations": [{
                "name": vm_name + '-ip-conf',
                "subnet": {"id": subnet_id},
                "public_ip_address": {
                    "id": ip_id}
            }],
            'network_security_group': {
                'id': nsg_id
            }
        }
    ).result()


def provision_vm(compute_cli, rg_name, vm_name, location, nic_id, sub_id, img_gallery):
    return compute_cli.virtual_machines.begin_create_or_update(
        rg_name,
        vm_name,
        {
            "location": location,
            "storage_profile": {
                "image_reference": {
                    "id": "/subscriptions/{0}/resourceGroups/TSM-CloudSys/providers/Microsoft.Compute/galleries/"
                          "{1}/images/{2}-img".format(sub_id, img_gallery, vm_name)
                }
            },
            "hardware_profile": {
                "vm_size": "Standard_DS1_v2"
            },
            "network_profile": {
                "network_interfaces": [{
                    "id": nic_id,
                }]
            }
        }
    ).result()


# Constants required for azure
SUB_ID = 'eb9915c7-85b9-45aa-b833-93ee8eefb218'
RESOURCE_GROUP = 'TSM-CloudSys-new'
SUBNET = 'default'
LOCATION = 'switzerlandnorth'
APP_NAME = 'todo'
DB_VM_NAME = APP_NAME + '-db'
API_VM_NAME = APP_NAME + '-api'
APP_VM_NAME = APP_NAME + '-app'
IMG_GALLERY = APP_NAME + '_img_gallery'
VNET = APP_NAME + '-vnet'

# Get the azure credentials
print("credentials...\t\t", end='')
credential = InteractiveBrowserCredential()
print("ok")

# Get the clients
print("clients...\t\t\t", end='')
resource_client = ResourceManagementClient(credential, SUB_ID)
compute_client = ComputeManagementClient(credential, SUB_ID)
network_client = NetworkManagementClient(credential, SUB_ID)
print("ok")

# Get the resource group
print("resource group...\t", end='')
rg = resource_client.resource_groups.create_or_update(RESOURCE_GROUP, {"location": LOCATION})
print("ok")

# Get the virtual network
print("vnet...\t\t\t\t", end='')
vnet = network_client.virtual_networks.get(
    RESOURCE_GROUP,
    VNET
)
print("ok")

# Get the subnet
print("subnet...\t\t\t", end='')
subnet = network_client.subnets.get(
    RESOURCE_GROUP,
    VNET,
    SUBNET
)
print("ok")

# Get the nsg
nsg = network_client.network_security_groups.get(
    RESOURCE_GROUP,
    APP_NAME + "-nsg",
)

# Provision the vms
for vm in [DB_VM_NAME, API_VM_NAME, APP_VM_NAME]:
    print(f"{vm} vm...\t\t", end='')
    app_ip_address = provision_ip(RESOURCE_GROUP, vm, LOCATION)
    app_nic = provision_nic(RESOURCE_GROUP, vm, LOCATION, subnet.id, app_ip_address.id, nsg.id)
    app_vm = provision_vm(compute_client, RESOURCE_GROUP, vm, LOCATION, app_nic.id, SUB_ID, IMG_GALLERY)
    print("ok")

# Hosts file
api_ip = network_client.public_ip_addresses.get(RESOURCE_GROUP, API_VM_NAME + '-ip').ip_address
print(f"Please add '{api_ip} todo-api' to your hosts file")
print("Windows - C:\\Windows\\System32\\drivers\\etc\\hosts")
print("Mac & Linux - /etc/hosts")

# App ip
app_ip = network_client.public_ip_addresses.get(RESOURCE_GROUP, APP_VM_NAME + '-ip').ip_address
print(f"The todo app's ip: {app_ip}")
