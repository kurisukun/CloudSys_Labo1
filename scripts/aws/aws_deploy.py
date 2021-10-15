import boto3
import os
import time

database_image_id = "ami-01bc430de916195d6"
api_image_id = "ami-00e2e76e957f3fa92"
front_image_id = "ami-0675051097a15b6dd"

front_sg_id = "sg-0784978bd4110bf53"
api_sg_id = "sg-0ad10eb50d94daf24"
database_sg_id = "sg-0c3681794ba284d9e"

db_startup_script = open(os.path.join(os.path.dirname(__file__), 'aws_db_deploy.sh'), 'r').read()
api_startup_script = open(os.path.join(os.path.dirname(__file__), 'aws_api_deploy.sh'), 'r').read()
front_startup_script = open(os.path.join(os.path.dirname(__file__), 'aws_front_deploy.sh'), 'r').read()

ec2 = boto3.resource('ec2')

# Create database
res = ec2.create_instances(
  ImageId="ami-02e136e904f3da870", 
  InstanceType="t2.micro", 
  MinCount=1, 
  MaxCount=1,
  KeyName="MyAmazonKeypair",
  SecurityGroupIds=[database_sg_id],
  UserData=db_startup_script
)

db_instance_id = res[0].id
print("Waiting 30s for database node to be initialized")
time.sleep(30)
db_instance = ec2.Instance(db_instance_id)

print(db_instance)
print(f'Database IP: {db_instance.public_ip_address}')

api_startup_script = api_startup_script.replace('$$$db_node_ip$$$', db_instance.public_ip_address)

# Create API backend
res = ec2.create_instances(
  ImageId="ami-02e136e904f3da870", 
  InstanceType="t2.micro", 
  MinCount=1, 
  MaxCount=1,
  KeyName="MyAmazonKeypair",
  SecurityGroupIds=[api_sg_id],
  UserData=api_startup_script
)

api_instance_id = res[0].id
print("Waiting 20s for api node to be initialized")
time.sleep(20)
api_instance = ec2.Instance(api_instance_id)

print(api_instance)
print(f'API IP: {api_instance.public_ip_address}')

front_startup_script = front_startup_script.replace('$$$api_node_ip$$$', api_instance.public_ip_address)

# Create Front backend
res = ec2.create_instances(
  ImageId="ami-02e136e904f3da870", 
  InstanceType="t2.micro", 
  MinCount=1, 
  MaxCount=1,
  KeyName="MyAmazonKeypair",
  SecurityGroupIds=[front_sg_id],
  UserData=front_startup_script
)

front_instance_id = res[0].id
print("Waiting 20s for front node to be initialized")
time.sleep(20)
front_instance = ec2.Instance(front_instance_id)

print(front_instance)
print(f'Front IP: {front_instance.public_ip_address}')
print(f'Access the app: http://{front_instance.public_ip_address}')