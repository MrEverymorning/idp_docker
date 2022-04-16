from os import name
import docker
from docker import client

client_docker = docker.from_env()

def create_jenkins_network():
    jenkins_network = client_docker.networks.create(
            name = "my_jenkins",
            check_duplicate = True
            )
    print("created jenkins network %s" % (jenkins_network))

try:
    create_jenkins_network()
except:
    print("jenkins network already exists, deleting and restarting")
    for network in client_docker.networks.list():
        network_name = network.name
        if network_name == "my_jenkins":
            network.remove()
            print("just removed the network successfully")
            create_jenkins_network()

try: 
    jenkins_Container = client_docker.containers.get('my_jenkins')
    if jenkins_Container:
        print("stopping previously active jenkins container")
        for container in client_docker.containers.list():
            container_name = container.name
            if container_name == "my_jenkins":
                container.remove(force = True)
except: 
    print('the my_jenkins container doesnt exist, will create')

print("building Jenkins file from Dockerfile in current directory")
client_docker.images.build(path = '.',
                    dockerfile="Dockerfile",
                    rm=True,
                    tag="mreverymorning/my_jenkins")

print("running Jenkins container")
client_docker.containers.run('mreverymorning/my_jenkins',
                    detach="True",
                    auto_remove=True,
                    # network="jenkins_network",
                    environment=["DOCKER_TLS_VERIFY=1"],
                    ports = {"8080/tcp": 8080,
                             "50000/tcp": 50000},
                    volumes = {
                        'jenkins-data': {'bind': '/var/jenkins_home', 'mode': 'rw'},
                        'jenkins-docker-certs':{'bind': '/certs/client', 'mode': 'ro'}
                        },
                    name = "my_jenkins"
                    )
