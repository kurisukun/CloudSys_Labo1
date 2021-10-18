# Delete the three instances created before
instances_name = ['todo-frontend', 'todo-backend', 'todo-mysql']

for instance in exo.compute.list_instances():
    if instances_name.contains(instance.name):
        instance.delete()

# We could probably retrieve the elastic IP and delete it
# Other than that, it's probably not a good practice to delete the security groups, or the private network ?
# Every other action is doable the same easy way, objects from exo.compute implement the delete() method