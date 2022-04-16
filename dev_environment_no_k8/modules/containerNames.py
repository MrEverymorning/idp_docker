#get containers names as a list or dict for future docker commands, etc.
#by default is ddev-app and ddev-core unless a project_name is entered. 

from docker import APIClient

def containerNames(project_name="ddev"):
    containerNames.dict = [
            {"name": project_name + "-app"},
            {"name": project_name + "-core"},
                ]
    containerNames.list = [
            project_name + "-app",
            project_name + "-core"
            ]

def FindContainerNames(postfix="all"):
    client = APIClient()

    containers = []
    allcontainers = client.containers(all=True)
    for container in allcontainers:
        if postfix == "all":
            containers.append(container['Names'][0][1:])
        else:
            if container['Names'][0].endswith(postfix):
                containers.append(container['Names'][0][1:])

    return(containers)
