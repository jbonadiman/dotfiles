#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))

source $scripts_path/zsh_functions

init_path=$HOME/docker_init.sh

if exists docker
then
  if [ ! -f $init_path ]
  then
    echo "
    #!/usr/bin/env sh

    DOCKER_DISTRO=\"\$WSL_DISTRO_NAME\"
    DOCKER_DIR=/mnt/wsl/shared-docker
    DOCKER_SOCK=\"\$DOCKER_DIR/docker.sock\"
    if [ ! -S \"\$DOCKER_SOCK\" ]; then
        mkdir -pm o=,ug=rwx \"\$DOCKER_DIR\"
        chgrp docker \"\$DOCKER_DIR\"
        /mnt/c/Windows/System32/wsl.exe -d \$DOCKER_DISTRO sh -c \"nohup sudo -b dockerd < /dev/null > \$DOCKER_DIR/dockerd.log 2>&1\"
        export DOCKER_HOST=\"unix://\$DOCKER_SOCK\"
    fi" > $init_path
  else
    echo docker init already exists, skipping generation...
  fi
else
  echo docker not installed, skipping docker init generation...
fi
