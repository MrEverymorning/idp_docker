# syntax=docker/dockerfile:1
FROM debian:bullseye
RUN apt update && apt install -y curl
#software-properties-common prevents an error that is not address in teh salt files
RUN apt-get install -y software-properties-common
RUN curl -fsSL -o /usr/share/keyrings/salt-archive-keyring.gpg https://repo.saltproject.io/py3/debian/11/amd64/latest/salt-archive-keyring.gpg && echo "deb [signed-by=/usr/share/keyrings/salt-archive-keyring.gpg arch=amd64] https://repo.saltproject.io/py3/debian/11/amd64/latest bullseye main" | tee /etc/apt/sources.list.d/salt.list
#I had a problem getting the salt-minion to start the minion, but this is because an image is not running, only a container is running.  I thought this was a policy-rc.d problem, but actually it is good to not have a running process until a docker run command is used.  This keeps the image more stable.  
#https://stackoverflow.com/questions/46247032/how-to-solve-invoke-rc-d-policy-rc-d-denied-execution-of-start-when-building
RUN apt-get update -y && apt install -y salt-minion salt-ssh && \
    apt-get clean all

#RUN sed -i "s|#master: salt|master: salt-master|g" /etc/salt/minion

ENTRYPOINT ["salt-minion", "-l", "debug"]

