#!/bin/bash

docker run \
    -it \
    --rm \
    --name salt-minion \
    --network="salt-master" \
    --network="salt-master" \
    --hostname="ddev-app" \
    recondockeradmin/ddev-app


#add --add-host, --dns-search... to make sure /etc/hosts and /etc/resolv.conf are updated
    #--link="salt-master" \
