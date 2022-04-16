
from .containerNames import containerNames
from subprocess import run
from docker import APIClient

def save_current_container_state(project_name=None):
    '''
    The two options here:
    1. Save the ddev images as the default recondockeradmin/ddev-app, etc.
    2. Save the [project_name] images as the project name recondockeradmin/[project_name]-app, etc. 
    '''
    if not project_name:
        print("no project name")
        containerNames("ddev")
        container_dict = containerNames.dict
        #first, delete the pki directory from both the livin gcontainers.  
        #/etc/salt/pki   directory
        #/etc/salt/minion_id  file
        for name in container_dict:
            deletePkiCmd = "docker exec -u 0 " + name['name'] + " rm -rf /etc/salt/pki"
            deleteIdCmd = "docker exec -u 0 " + name['name'] + " rm -f /etc/salt/minion_id"
            run([deletePkiCmd],
                             capture_output = True,
                             shell=True,
                             text = True)
            run([deleteIdCmd],
                             capture_output = True,
                             shell=True,
                             text = True)

        print("getting container ID's for ddev")
        client = APIClient()
        container_ids = []
        containerNames()
        container_dict = containerNames.dict
        container_dict.append({"name":"salt-master"})

        for name in container_dict:
            print(name)
            output = (client.containers(filters = name,
                                        quiet = True))
            my_tuple = (name["name"], output.pop(0)["Id"])
            container_ids.append(my_tuple)

        print("Saving container images")
        for name, id in container_ids:
            print("Saving: %s" % name)
            client.commit(id,
                          repository = "recondockeradmin/" + name)
            #Then, delete the containers to force the user to restart
            docker_rm_containers_cmd = f"docker rm -f {name}"
            rm_containers = run([docker_rm_containers_cmd],
                                capture_output = True,
                                shell=True,
                                text = True)

    elif project_name:
        print(f"saving containers for {project_name} to recondockeradmin/{project_name}")
        client = APIClient()
        container_ids = []
        containerNames(project_name)
        container_dict = containerNames.dict
        for name in container_dict:
            output = (client.containers(
                filters = name,
                quiet = True
                ))
            my_tuple = (name["name"], output.pop(0)["Id"])
            container_ids.append(my_tuple)

        print("Saving container images")
        for name, id in container_ids:
            client.commit(
                    id,
                    repository = "recondockeradmin/" + name
                    )

    # except:
        # print("please be sure your are typing your project_name correctly")
