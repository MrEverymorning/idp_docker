#!/usr/bin/env python3
'''
This script is designed to set up a local dev environment,
and also has other features useful for developers
Be sure to have docker and tmux installed on your host before running. 
'''


# in this main script, I only want tmux and docker-compose
# other useful functions should be modules

from argparse import ArgumentParser, SUPPRESS
from subprocess import run
from libtmux import Server
from os import environ, path, remove, symlink, chdir, system
from time import sleep
from docker import APIClient
# from socket import socket, AF_INET, SOCK_STREAM
from shutil import copy
from modules.findPorts import findPort1, findPort2
from modules.network import create_project_network
from modules.saveContainerState import save_current_container_state
from modules.containerNames import FindContainerNames
from modules.remove import rm_network_and_containers, rm_all_network_and_containers
from modules.waitFindContainer import waitForContainers, findContainer, findSaltMaster

#tmux server
server = Server()

def parse_args():
    parser = ArgumentParser(description= 'Starts local containerized dev environment')

    parser.add_argument('-s', '--from_scratch', dest='FromScratch', 
                        action='store_true', help='Rebuild images from scratch')
    parser.add_argument('-p', '--from_dockerhub', dest='FromDockerhub',
                        action='store_true', help='pull post-highstate image from DockerHub')
    parser.add_argument('-l', '--from_local', dest='FromLocal', 
                        action='store_true', help='use pulled images from dockerhub. Will only work if you already pulled from dockerhub once')
    parser.add_argument('-t', '--highstate', dest='highstate', 
                        action='store_true', help='run the highstate commands in parallel once the containers are successfully running')
    parser.add_argument('-i', '--image_save', dest='Image_Save', 
                        action='store_true', help='save the current state off ddev-app and ddev-core containers as the new local image')
    parser.add_argument('--save_project_image', type=str, 
                        help='save a project to a custom image recondockeradmin/[project_name]-app, etc')
    parser.add_argument('--deploy_static', dest='DeployStatic',
                        action='store_true', help='Deploy static files to app')
    parser.add_argument('-c', '--new_cluster', dest='new_cluster', type=str, help='Deploy static files to app')
    parser.add_argument('--remove_containers', dest='remove_containers', action='store_true',
                        help='Deploy static files to app')
    parser.add_argument('--multi-network', dest='multi_network', 
                        type=int, help='Deploy a test multi-network.  Always sets up networks salt-master, and prime.  Add a number 1-3 for additional networks test1, test2.  hostnames will be test1-app, etc.')
    parser.add_argument('--hs-multi-network', dest='hs_multi_network', action='store_true',
                        help='will highstate running networks.')
    parser.add_argument('--save-multi-network', dest='save_multi_network', action='store_true',
                        help='save images for running networks.')
    parser.add_argument('--reconpy', dest='reconpy', action='store_true',
                        help='Run recon.py in all running core containers')
    parser.add_argument('--startapp', dest='startapp', action='store_true',
                        help='Run app start commands on all app containers')
    parser.add_argument( '-m', '--salt-master', dest='salt_master', action='store_true',
                        help='salt-master testing')

    args = parser.parse_args()
    if len([ k for (k,v) in vars(args).items() if v]) == 0:
        print("No Arguments")
        parser.print_help()
        exit()
    return args

HOME = environ['HOME']
current_dir = HOME + "/recon/tv/dev-setup/dev_environment_no_k8"
cwd_current = current_dir + "/current"
cwd_scratch = current_dir + "/docker_compose_scratch"
cwd_pull = current_dir + "/docker_compose_pull"
cwd_local = current_dir + "/docker_compose_local"
cwd_multi_network = current_dir + "/docker_compose_prime"

def create_symlink(source):
    if path.exists(cwd_current):
        remove(cwd_current)
    symlink(source, cwd_current)

def startSaltMaster():
    # print("checking if salt-master is already running.")
    create_project_network("salt-master")
    if findSaltMaster("salt-master") == True:
        print("salt-master already running")
    else:
        if server.has_session("salt-master"):
            highstate_session = server.kill_session(target_session='salt-master')
        print("starting salt-master")
        cmd = "docker-compose -f salt-master-compose.yml up"
        # run([cmd],
                # capture_output=True,
                # shell = True,
                # text = True)
        session = server.new_session(session_name="salt-master")
        session.new_window(window_name="salt-master",
                           start_directory=cwd_multi_network,
                           attach=False,
                           window_shell=cmd)
        print("salt-master should be running now")

def multi_network(netnum):
    create_symlink(cwd_multi_network)
    startSaltMaster()
    findContainer('salt-master')
    # Clear salt keys
    cmd = "docker exec -u 0 salt-master salt-key -Dy"
    run([cmd],
        capture_output = True,
        shell = True,
        text = True)
    client = APIClient()


    #second start prime network with compose() with the project names from the multi-network list
    for cnt in range(netnum):
        print(cnt)
        if cnt == 0:
            network = 'prime'
        else:
            network = 'test' + str(cnt)
        if client.images(name=f"recondockeradmin/{network}-app"):
            print(f"image for {network} exists")
            make_compose_yml(network, network)
        else:
            make_compose_yml(network)
        rm_network_and_containers(network)
        compose(arg="new_project_local", project_name=network, create_network=True)

def highstateMultinetwork():
    print("highstating networks to properly adjust hostnames to container names")
    cmd = "docker exec salt-master salt *-app state.highstate"
    highstate = run([cmd],
        capture_output = True,
        shell = True,
        text = True)

def saveMultiNetwork():
    containerNames = [
                    {"name": "prime-app"},
                    {"name": "prime-core"},
                    {"name":    "test1-app"},
                    {"name":   "test1-core"},
                    {"name":    "test2-app"},
                    {"name":    "test2-core"},
                    ]
    client = APIClient()
    container_ids = []
    for name in containerNames:
        print(f"getting {name}'s container ID")
        output = client.containers(filters = name,
                                   quiet = True)
        saveTuple = (name["name"], output.pop(0)["Id"])
        print()
        container_ids.append(saveTuple)

    print("Saving container images")
    print(container_ids)
    for name, id in container_ids:
        print("Saving {name}")
        print(name, id)
        client.commit(id, repository="recondockeradmin/" + name)

    numberOfContainerNetworks = int(len(container_ids)/2)
    print(numberOfContainerNetworks)
    print('''
        Saved a custom image for each container!
        Restarting each container with it's own custom image!
            ''')
    multi_network(numberOfContainerNetworks)

def runReconPy():
    containerNames = FindContainerNames("core")

    for name in containerNames:
        cmd = f"docker exec {name} recon.py"
        print(cmd)
        run([cmd],
            capture_output = True,
            shell = True,
            text = True)

def startApplication():
    containerNames = FindContainerNames("app")
    # Start nginx
    # Start supervisord
    cmds = ["/etc/init.d/nginx start",
            "supervisord",
            'sudo su - tvadmin -c "source /opt/recon/tv/webapp/bin/activate && cd /opt/recon/tv/webapp/src/tvwebapp && source /opt/recon/tv/webapp/src/tvwebapp/bin/django_bash_completion.sh && export DJANGO_SETTINGS_MODULE=tvw.settings.instance && supervisorctl stop webapp:uwsgi"',
            'sudo su - tvadmin -c "source /opt/recon/tv/webapp/bin/activate && cd /opt/recon/tv/webapp/src/tvwebapp && source /opt/recon/tv/webapp/src/tvwebapp/bin/django_bash_completion.sh && export DJANGO_SETTINGS_MODULE=tvw.settings.instance && da start_app"']

    for container in containerNames:
        for cmd in cmds:
            cmdstr = f"docker exec {container} {cmd}"
            result = run([cmdstr],
                         capture_output = True,
                         shell = True,
                         text = True)
            print(result.stdout)

    # Stop webapp:uwsgi
    # Django start_app command
    pass

def make_compose_yml(ddev_replacement, image_replacement="ddev"):
    port_1 = findPort1()
    port_2 = findPort2()
    copy("./current/compose-template.yml", "/tmp/compose.yml" )
    with open(r'/tmp/compose.yml', 'r') as file:
        data = file.read()
        data = data.replace("port_1", port_1)
        data = data.replace("port_2", port_2)
        data = data.replace("project_name", ddev_replacement)
        data = data.replace("project_image", image_replacement)

    with open(r'/tmp/compose.yml', 'w') as file:
        file.write(data)

    print("compose file ready, starting cluster")

def compose(arg=None, project_name="ddev", create_network=False):
    if create_network:
        create_project_network(project_name)

    #set the compose command for the tmux window based on user intent
    if arg == "from_scratch":
        cmd = "docker-compose up --build; read"
    elif arg == "local":
        cmd = "docker-compose up; read"
    elif arg == "project_from_scratch":
        cmd = f"docker-compose -f /tmp/compose.yml --project-name {project_name} up --build; read"
    elif arg == "new_project_local":
        cmd = f"docker-compose -f /tmp/compose.yml --project-name {project_name} up"

    print("\t your docker command is: %s" % cmd)
        
    #tmux highstate and docker-compose kill and start for scratch and local

    # tmux project highstate and docker-compose kill and start
    if server.has_session(f"{project_name}_highstate"):
        print(f"\t\tkilling previous highstate tmux session for {project_name}")
        highstate_session = server.kill_session(target_session=f'{project_name}_highstate')

    if server.has_session(f"{project_name}_DockerCompose"):
        print(f"killing previous DockerCompose tmux session for {project_name}")
        highstate_session = server.kill_session(target_session=f'{project_name}_DockerCompose')

    print(f"Starting tmux session now for {project_name}...")
    session = server.new_session(session_name=f"{project_name}_DockerCompose")

    print(f"running Docker Compose for {project_name}")
    session.new_window(window_name=f"{project_name}",
                       start_directory=cwd_current,
                       attach=False,
                       window_shell=cmd
    )

    try: 
        session.kill_window("bash")
    except:
        pass

    waitForContainers(project_name)

def start_tmux_hs(project_name="ddev"):
    container_list = FindContainerNames()

    if server.has_session(f"{project_name}_highstate"):
        print("killing previous highstate tmux session")
        highstate_session = server.kill_session(target_session=f'{project_name}_highstate')
    print(f"Starting tmux session now for {project_name}")
    session = server.new_session(session_name=f"{project_name}_highstate")

    #highstate the minions
    for container in container_list:
        print("New tmux window for %s" % container)
        session.new_window(window_name=container,
                start_directory=cwd_current,
                attach=False,
                window_shell='docker-compose exec salt-master salt -l debug %s state.highstate; read' % container)

    # kill_unnecessary_windows(project_name)
    try:
        session.kill_window("bash")
    except:
        pass

def kill_unnecessary_windows(project_name):
    #close the stale tmux bash window
    session = server.new_session(session_name=f"{project_name}_highstate")
    try: 
        session.kill_window("bash")
    except:
        pass
    try:
        session.kill_window("zsh")
    except:
        pass
    windows = server._list_windows()
    running_sessions_windows = []
    for a in windows:
        for elem in a.values():
            running_sessions_windows.append(elem) 

    # if "highstate" and "ddev-core" and "ddev-app" in running_sessions_windows:
    if f"{project_name}-core" and f"{project_name}-app" in running_sessions_windows:
        print(f"tmux has begun the highstate of {project_name}-core and {project_name}-app successfully")
    else:
        print("Tmux has not started correctly.  Please run this script one more time. ")

def deploy_static():
    # this command should only be run when starting app for the first time, before
    # any images are saved. 
    cmd = 'docker-compose exec salt-master salt ddev-app state.sls tv.webapp.utils'
    chdir(cwd_current)
    system(cmd)

def main():
    args = parse_args()

    if args.salt_master:
        startSaltMaster()

    elif args.multi_network:
        symlink
        multi_network(args.multi_network)

    elif args.new_cluster:
        project = args.new_cluster
        print(f"\tyour project name is {project}")

        if args.remove_containers:
            print(f"removing containers and network for project {project}")
            rm_network_and_containers(project)
            quit()

        if args.FromScratch:
            create_symlink(cwd_scratch)

        elif args.FromLocal:
            create_symlink(cwd_local)
        rm_network_and_containers(project)
        make_compose_yml(project)
        compose(arg="new_project_current_dir", project_name=project)

    elif args.FromScratch:
        create_symlink(cwd_scratch)
        rm_all_network_and_containers()
        compose(arg="from_scratch")

    elif args.FromLocal:
        create_symlink(cwd_local)
        rm_network_and_containers()
        compose(arg="local")

    if args.remove_containers:
        rm_network_and_containers()

    if args.Image_Save:
        save_current_container_state()
    if args.save_project_image:
        save_current_container_state(args.save_project_image)

    if args.hs_multi_network:
        highstateMultinetwork()

    if args.save_multi_network:
        saveMultiNetwork()

    if args.reconpy:
        runReconPy()

    if args.startapp:
        startApplication()

    if args.highstate:
        if args.new_cluster:
            start_tmux_hs(args.new_cluster)
        else:
            start_tmux_hs()
        print('''
            Containers have sucessfully started with their minions. 
            The containers are now highstating in a detached tmux session. 
            highstate for ddev-app will be run twice automatically, until order error is fixed. 
            If you would like to see the output, and you were not previously running tmux,
            type this command to see the window: 

            tmux attach
            and use "Ctrl+b" "n" to switch between tmux windows. 
            
            to go back to your terminal:
            tmux detach

            if you were already running tmux, you can view and switch to the new "highstate"
            session by using:
            tmux choose-tree

                ''')
    print('''
        useful commands: 

        remove all current containers
        docker rm -f $(sudo docker ps -a -q)


            ''')

    # If you need to clean all your images/containers:
    # docker ps -q | xargs docker stop
    # docker ps -q | xargs docker rm
    # docker rm $(docker ps --filter "status=exited" -q)
    # docker rmi $(docker images -a -q)

    if args.DeployStatic:
        deploy_static()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
 
