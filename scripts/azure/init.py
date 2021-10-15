from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import NetworkSecurityGroup, SecurityRule
from azure.mgmt.compute import ComputeManagementClient

# Constants required for azure
SUB_ID = 'eb9915c7-85b9-45aa-b833-93ee8eefb218'
RESOURCE_GROUP = 'TSM-CloudSys-new'
APP_NAME = 'todo'
LOCATION = 'switzerlandnorth'

# Acquire azure credentials
print("credentials... ", end='')
credential = InteractiveBrowserCredential()

# Acquire clients
print("clients... ", end='')
resource_client = ResourceManagementClient(credential, SUB_ID)
compute_client = ComputeManagementClient(credential, SUB_ID)
network_client = NetworkManagementClient(credential, SUB_ID)
print("ok")

# Provision the resource group
print("resource group... ", end='')
rg = resource_client.resource_groups.create_or_update(RESOURCE_GROUP, {"location": LOCATION})
print(f"ok: {rg.name}")

# Provision the virtual network
print("vnet... ", end='')
vnet = network_client.virtual_networks.begin_create_or_update(
    RESOURCE_GROUP,
    APP_NAME + '-vnet',
    {
        "location": LOCATION,
        "address_space": {
            "address_prefixes": ["10.0.0.0/16"]
        }
    }
).result()
print(f"ok: {vnet.name} - {vnet.address_space.address_prefixes}")

# Provision the subnet
print("subnet... ", end='')
subnet = network_client.subnets.begin_create_or_update(
    RESOURCE_GROUP,
    APP_NAME + "-vnet",
    "default",
    {"address_prefix": "10.0.0.0/24"}
).result()
print(f"ok: {subnet.name} - {subnet.address_prefix}")

# Provision the nsg
print("nsg... ", end='')
parameters = NetworkSecurityGroup()
parameters.location = LOCATION
parameters.security_rules = [
    SecurityRule(name='HTTP',  provisioning_state='Succeeded', protocol='TCP',  source_port_range='*', destination_port_range='80',   source_address_prefix='*', destination_address_prefix='*', access='Allow', priority='1000', direction='Inbound', source_port_ranges=[], destination_port_ranges=[], source_address_prefixes=[], destination_address_prefixes=[]),
    SecurityRule(name='MySQL', provisioning_state='Succeeded', protocol='TCP',  source_port_range='*', destination_port_range='3306', source_address_prefix='*', destination_address_prefix='*', access='Allow', priority='1010', direction='Inbound', source_port_ranges=[], destination_port_ranges=[], source_address_prefixes=[], destination_address_prefixes=[]),
    SecurityRule(name='SSH',   provisioning_state='Succeeded', protocol='TCP',  source_port_range='*', destination_port_range='22',   source_address_prefix='*', destination_address_prefix='*', access='Allow', priority='1020', direction='Inbound', source_port_ranges=[], destination_port_ranges=[], source_address_prefixes=[], destination_address_prefixes=[]),
    SecurityRule(name='ICMP',  provisioning_state='Succeeded', protocol='ICMP', source_port_range='*', destination_port_range='*',    source_address_prefix='*', destination_address_prefix='*', access='Allow', priority='1030', direction='Inbound', source_port_ranges=[], destination_port_ranges=[], source_address_prefixes=[], destination_address_prefixes=[]),
]
nsg = network_client.network_security_groups.begin_create_or_update(
    RESOURCE_GROUP,
    APP_NAME + "-nsg",
    parameters,
).result()
print(f"ok: {nsg.name}")
