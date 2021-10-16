import google.cloud.compute_v1 as compute_v1
from google.cloud.compute_v1.types import *
import google.auth
import uuid
import time
import os

def wait_for_operation(project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute_v1.ZoneOperationsClient().get(project=project, zone=zone, operation=operation)
        if result.status == Operation.Status.DONE:
            print("done.")
            if 'error' in result:
                raise Exception(result.error)
            return result
        time.sleep(1)


credentials , project_id = google.auth.default()

#Google Cloud Constants
ZONE = "us-west4-b"
MACHINE_TYPE = "e2-medium"
PROJECT = "healthy-icon-328807"
#Instances Constants
UUID = uuid.uuid4().hex[:10]
DB_NAME = "db-" + UUID
BACKEND_NAME = "backend-" + UUID
BACKEND_SCRIPT = "backend_script.sh"
FRONTEND_NAME = "frontend-" + UUID
FRONTEND_SCRIPT = "frontend_script.sh"


# [START] Database
instance_client = compute_v1.InstancesClient()

disk = compute_v1.AttachedDisk()
initialize_params = compute_v1.AttachedDiskInitializeParams()
initialize_params.disk_size_gb = 20
initialize_params.source_image = "projects/healthy-icon-328807/global/images/image-db"
disk.initialize_params = initialize_params
disk.auto_delete = True
disk.boot = True
access_config = compute_v1.AccessConfig()

network_interface = compute_v1.NetworkInterface()
network_interface.access_configs = [access_config]


instance = compute_v1.Instance()
tags = compute_v1.Tags()
tags.items = ["firewall-db", "firewall-out"]
instance.name = DB_NAME
instance.disks = [disk]
instance.tags = tags
full_machine_type_name = f"zones/{ZONE}/machineTypes/{MACHINE_TYPE}"
instance.machine_type = full_machine_type_name
instance.network_interfaces = [network_interface]

request = compute_v1.InsertInstanceRequest()
request.zone = ZONE
request.project = project_id
request.instance_resource = instance

op = instance_client.insert(request)

wait_for_operation(PROJECT, ZONE, op.name)
print("Ok DB")
# [END] Database



# [START] Backend
instance_client = compute_v1.InstancesClient()

disk = compute_v1.AttachedDisk()
initialize_params = compute_v1.AttachedDiskInitializeParams()
initialize_params.disk_size_gb = 10
initialize_params.source_image = "projects/healthy-icon-328807/global/images/image-backend"
disk.initialize_params = initialize_params
disk.auto_delete = True
disk.boot = True

access_config = compute_v1.AccessConfig()
network_interface = compute_v1.NetworkInterface()
network_interface.access_configs = [access_config]

instance = compute_v1.Instance()
instance.name = BACKEND_NAME
tags = compute_v1.Tags()
tags.items = ["firewall-backend", "firewall-out"]
instance.tags = tags
# GET DB IP ADDRESS
request = compute_v1.GetInstanceRequest()
request.instance = DB_NAME
request.project = PROJECT
request.zone = ZONE
op = instance_client.get(request)
#wait_for_operation(PROJECT, ZONE, op.name)
db_ip = op.network_interfaces[0].network_i_p

backend_script = open(os.path.join(os.path.dirname(__file__), BACKEND_SCRIPT), 'r').read()
backend_script = backend_script.replace("$__IP_DB_HOST__$", db_ip)
metadata = compute_v1.Metadata()
metadata.items = [{"key": "startup-script", "value": backend_script}]
instance.metadata = metadata
instance.disks = [disk]

full_machine_type_name = f"zones/{ZONE}/machineTypes/{MACHINE_TYPE}"
instance.machine_type = full_machine_type_name
instance.network_interfaces = [network_interface]

request = compute_v1.InsertInstanceRequest()
request.zone = ZONE
request.project = project_id
request.instance_resource = instance

op = instance_client.insert(request)
wait_for_operation(PROJECT, ZONE, op.name)
print("Ok BACKEND")
# [END] Backend



# [START] Frontend
instance_client = compute_v1.InstancesClient()

disk = compute_v1.AttachedDisk()
initialize_params = compute_v1.AttachedDiskInitializeParams()
initialize_params.disk_size_gb = 20
initialize_params.source_image = "projects/healthy-icon-328807/global/images/image-frontend"
disk.initialize_params = initialize_params
disk.auto_delete = True
disk.boot = True
access_config = compute_v1.AccessConfig()

network_interface = compute_v1.NetworkInterface()
network_interface.access_configs = [access_config]


instance = compute_v1.Instance()
instance.name = FRONTEND_NAME
tags = compute_v1.Tags()
tags.items = ["firewall-frontend", "firewall-out"]
instance.tags = tags
# GET BACKEND IP ADDRESS
request = compute_v1.GetInstanceRequest()
request.instance = BACKEND_NAME
request.project = PROJECT
request.zone = ZONE
op = instance_client.get(request)
backend_ip = op.network_interfaces[0].access_configs[0].nat_i_p
frontend_script = open(os.path.join(os.path.dirname(__file__), FRONTEND_SCRIPT), 'r').read()
frontend_script = frontend_script.replace("$__IP_BACKEND_HOST__$", backend_ip)

metadata = compute_v1.Metadata()
metadata.items = [{"key": "startup-script", "value": frontend_script}]
instance.metadata = metadata

instance.disks = [disk]
full_machine_type_name = f"zones/{ZONE}/machineTypes/{MACHINE_TYPE}"
instance.machine_type = full_machine_type_name
instance.network_interfaces = [network_interface]

request = compute_v1.InsertInstanceRequest()
request.zone = ZONE
request.project = project_id
request.instance_resource = instance

op = instance_client.insert(request)
wait_for_operation(PROJECT, ZONE, op.name)
# [END] Frontend
print("Ok FRONT")


request = compute_v1.GetInstanceRequest()
request.zone = ZONE
request.project = project_id
request.instance = FRONTEND_NAME
res = instance_client.get(request)

app_ip = res.network_interfaces[0].access_configs[0].nat_i_p

print(f'You can connect to the app here: http://{app_ip}')