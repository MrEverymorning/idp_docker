
from .containerNames import containerNames
from docker import APIClient
from time import sleep

def waitForContainers(project_name):
    containerNames(project_name)
    container_dict = containerNames.dict
    # Wait for conatainers to start
    for name in container_dict:
        contname = name['name']
        print(contname)
        findContainer(contname)
    # Give a few seconds for salt minions to start
    sleep(3)

def findContainer(ContName):
    client = APIClient()
    print(f"Looking for {ContName}")
    # for _ in range(5):
    notFound = True
    while notFound:
        cc = client.containers()
        for running in cc:
            if ['/' + ContName] in running.values():
                print('Found %s' % ContName)
                notFound = False
                break
                # return True
            if notFound:
                sleep(1)
    return False

def findSaltMaster(ContName):
    client = APIClient()
    print(f"Looking for {ContName}")
    for _ in range(2):
        cc = client.containers()
        for running in cc:
            if ['/' + ContName] in running.values():
                print('Found %s' % ContName)
                return True
            else:
                sleep(1)
    print(f"couldn't find {ContName}")
    return False

def findSaltMasterNetwork(ContName):
    client = APIClient()
    print(f"Looking for network {ContName}")
    # print(client.networks())
    for _ in range(2):
        cc = client.networks()
        for running in cc:
            if ContName in running.values():
                print('Found network %s' % ContName)
                return True
            # else:
                # sleep(1)
    print(f"couldn't find network {ContName}")
    return False

def findImage(ContName):
    client = APIClient()
    containerNames(ContName)
    container_dict = containerNames.dict
    for name in container_dict:
        # print(name.values())
        imageName = f"recondockeradmin/{name['name']}:latest"
        print(f"Looking for image {imageName}")
        cc = client.images()
        for running in cc:
            # print(running.values())
            if [imageName] in running.values():
                print('Found image for %s-app, assuming core is there as well' % ContName)
                return True
            # else:
                # print("nope")
                # sleep(1)
        print(f"couldn't find image {imageName}, you'll need to finish following the google-doc")
        return False
