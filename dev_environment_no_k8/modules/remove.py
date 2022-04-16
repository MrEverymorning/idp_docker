
from .containerNames import containerNames
from subprocess import run

def rm_network_and_containers(project_name="ddev"):
    containerNames(project_name)
    container_dict = containerNames.dict

    for container in container_dict:
        print("removing %s" % container['name'])
        docker_rm_container = "docker rm -f " + container['name']
        run([docker_rm_container],
            capture_output = True,
            shell=True,
            text = True)

    docker_rm_network = f"docker network rm {project_name}_default"
    run([docker_rm_network],
        capture_output = True,
        shell=True,
        text = True)
def rm_all_network_and_containers():
    docker_rm_containers = "docker rm -f $(docker ps -a -q)"
    docker_rm_networks = "docker network rm $(docker ls -q)"

    print("killing all previous networks and containers...")
    kill_all_containers =run([
            docker_rm_containers
            ],
            capture_output = True,
            shell=True,
            text = True)

    kill_all_docker_networks =run([
            docker_rm_networks
            ],
            capture_output = True,
            shell=True,
            text = True)

