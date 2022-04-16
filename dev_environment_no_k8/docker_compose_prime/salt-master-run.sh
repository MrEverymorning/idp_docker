#!/bin/bash

#make the salt-master network here
# The Docker documentation doesn't explain why the bridge network is used to create a new network
docker network create -d bridge salt-master
#docker network create -d bridge prime
#docker network create -d bridge test1
#docker network create -d bridge test2
#docker network create -d bridge test3

tmux neww -n "salt-master" docker run \
    -it \
    --rm \
    --name salt-master \
    --mount type=bind,source=$HOME/recon/tv/tvsalt,target=/srv/salt \
    --mount type=bind,source=$HOME/recon/tv/tvpillar-dev,target=/srv/pillar \
    --mount type=bind,source=$HOME/recon/tv,target=/opt/recon/tv \
    --network="salt-master" \
    --hostname="salt-master" \
    recondockeradmin/salt-master

#add --add-host, --dns-search... to make sure /etc/hosts and /etc/resolv.conf are updated
