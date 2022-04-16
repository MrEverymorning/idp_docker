from docker import APIClient

def create_project_network(project_name):
    client = APIClient()

    # only create a new network for project_name if it doesn't already exist
    currentNetworks = client.networks()
    for network in currentNetworks:
        if network["Name"] == f"{project_name}":
            print(f"{project_name} network already exists!")
            return True
        else:
            pass

    print(f"{project_name} network does not yet exist, creating now...")
    client.create_network(project_name)
    print(f"{project_name} network is now running!")
