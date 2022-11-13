#!/usr/bin/env sh
DOCKER_DISTRO=Arch
DOCKER_DIR=/mnt/wsl/shared-docker
DOCKER_SOCK=/mnt/wsl/shared-docker/docker.sock
if [ ! -S "$DOCKER_SOCK" ]; then
  mkdir -pm o=,ug=rwx "$DOCKER_DIR"
  chgrp docker "$DOCKER_DIR"
  wsl.exe -d $DOCKER_DISTRO sh -c "nohup sudo -b dockerd < /dev/null > $DOCKER_DIR/dockerd.log 2>&1"
fi
