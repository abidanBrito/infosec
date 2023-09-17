#!/usr/bin/env bash

source color.sh

# Docker registry + image
DREG=extgit.iaik.tugraz.at:8443
DREGUSER=ssddocker
DREGTOKEN=RyuKLkKystQVtxsZ_Za3
DIMG=$DREG/infosec/assignments2022:docker-infosec

EXPLOIT_DIR_SRC="${PWD}/$2"
EXPLOIT_DIR_DST="/app"
EXPLOIT_VOLATILE_DIR="/tmp/app"

SCRIPT=execute_permissions.sh
DBGSCRIPT=dbg_exploit.sh

function docker_image_exists {
  debug_info "GREEN" "Check whether docker image exists"
  docker run -t $DIMG /usr/bin/whoami &> /dev/null
  if [[ "$?" -ne "0" ]];
  then
    debug_info "LIGHT_RED" "Docker image does not exists"
    return 1
  else
    debug_info "GREEN" "Docker image exists"
    return 0
  fi
}

function build_image {
  ret_val=0

  debug_info "GREEN" "Logging into Docker registry"
  docker login -u $DREGUSER -p $DREGTOKEN $DREG || ret_val=$?

  debug_info "GREEN" "Pulling Docker image"
  docker pull $DIMG || ret_val=$?
  docker logout $DREG || ret_val=$?

  debug_info "GREEN" "Trying to run Docker image"
  docker run -t $DIMG /usr/bin/whoami &> /dev/null || ret_val=$?
  if [[ "$ret_val" -ne "0" ]];
  then
    debug_fail "Could not build docker image $DREG"
  else
    debug_info "GREEN" "Successfully updated Docker image:"
    docker image inspect $DIMG | grep Created || ret_val=$?
  fi

  return $ret_val
}

function docker_update {
  build_image
  ret_value="$?"
  if [[ "$ret_value" -ne "0" ]]
  then
    debug_fail "return value was $ret_value"
    exit $ret_value
  fi
}

function docker_build {
  docker_image_exists
  if [[ "$?" -ne "0" ]]
  then
    docker_update
  fi
}

function run {
  debug_info "GREEN" "run docker image"
  CMD="mkdir -p $EXPLOIT_VOLATILE_DIR; cp -r $EXPLOIT_DIR_DST/* $EXPLOIT_VOLATILE_DIR; cd $EXPLOIT_VOLATILE_DIR; "
  CMD+="./$SCRIPT; "
  CMD+="zsh; "
  docker run \
    -v "$EXPLOIT_DIR_SRC:$EXPLOIT_DIR_DST" \
    --rm \
    -it $DIMG \
    sh -c "$CMD"
}

function dbg {
  debug_info "GREEN" "run docker image"
  CMD="mkdir -p $EXPLOIT_VOLATILE_DIR; cp -r $EXPLOIT_DIR_DST/* $EXPLOIT_VOLATILE_DIR; cd $EXPLOIT_VOLATILE_DIR; "
  CMD+="./$DBGSCRIPT; "
  CMD+="zsh; "
  docker run \
    --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
    -v "$EXPLOIT_DIR_SRC:$EXPLOIT_DIR_DST" \
    --rm \
    -it $DIMG \
    sh -c "$CMD"
}

function print_usage {
  debug_info "LIGHT_BLUE" "Usage:"
  debug_info "LIGHT_BLUE" "  $0 run <dir>"
  debug_info "LIGHT_BLUE" "  $0 help"
  debug_info "LIGHT_BLUE" "  $0 update"
  debug_info "LIGHT_BLUE" "  $0 debug"
}

function print_info {
  debug_info "YELLOW" "1. All files in /tmp/app are volatile."
  debug_info "YELLOW" "2. $EXPLOIT_DIR_SRC is mounted"
  debug_info "YELLOW" "   in /app. Changes are permanent."
  debug_info "YELLOW" "3. Currently you are user root. If you want"
  debug_info "YELLOW" "   to execute an exploit you need to change to user"
  debug_info "YELLOW" "   exploit (execute su exploit)."
  debug_info "YELLOW" "4. To start a hacklet just call $SCRIPT."
}

if [[ "$#" -eq "0" || "$1" == "help" ]];
then
  print_usage
elif [[ "$1" == "run" ]];
then
  docker_build &&\
  print_info &&\
  run "$2"
elif [[ "$1" == "update" ]];
then
  docker_update
elif [[ "$1" == "debug" ]];
then
  docker_build &&\
  print_info &&\
  dbg "$2"
else
  debug_fail "Unkown command"
  exit 1
fi
