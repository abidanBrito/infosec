#PowerShell adaption of the docker.sh script

$DREG="extgit.iaik.tugraz.at:8443"
$DREGUSER="ssddocker"
$DREGTOKEN="RyuKLkKystQVtxsZ_Za3"
$DIMG=$DREG+"/sase/practicals/docker:docker-infosec"

$RED='\033[0;31m'
$YELLOW='\033[1;33m'
$BLUE='\033[1;34m'
$NC='\033[0m' # No Color



function error {
  printf "${RED}$*${NC}\n"
}

function warning {
  printf "${YELLOW}$*${NC}\n"
}

function info {
  printf "${BLUE}$*${NC}\n"
}

# This function pulls the latest ssd Docker image from the upstream
# Docker registry
function docker_update() {
  $r=$true
  echo "Logging into Docker registry"
  docker login -u ${DREGUSER} -p ${DREGTOKEN} ${DREG}
  echo "Pulling Docker image"
  docker pull ${DIMG}
    if(!$?){
    $r = $false
    }
  docker logout ${DREG}
  
  echo "Trying to run Docker image"
  docker run -t ${DIMG} /usr/bin/whoami > $null
    if(!$?)
    {
        $r = $false
    }
    if($r -eq $true)
    {
        echo "Successfully updated Docker image:"
        docker image inspect ${DIMG} | Select-String Created
    }
    else
    {
        echo "Update failed"
        exit 1
    }

}



if ( $args.length -eq 0 -or $args[0] -eq "help" ){
  # Show help
  echo "This script runs your code inside Docker"
  echo ""
  echo "./docker.ps1 help       Show this help"
  echo "./docker.ps1 update     Pull the latest Docker image from the ssd2019 registry"
  echo "./docker.ps1 run [<dir>]  Run Docker inside the current directory, or <dir>, if provided"
  echo ""
  exit 0
 }

 elseif( $args[0] -eq "update" ){
  # Force an update of the Docker image
  docker_update
  exit 0

  }

elseif( $args[0] -eq "run")
{
    if($args.Length -eq 2)
    {
        cd $args[1]
    }
}
else
{
    echo "Invalid argument"
    exit 1
}

docker --help > $null
if(!$?)
{
  echo "Please install docker first"
  exit 1
}

docker run --rm -t ${DIMG} /usr/bin/whoami > $null
if(!$?)
{
  warning "Docker image missing"
  docker_update
}

$CMD="mkdir ssd; cd ssd; cp -r /mnt/host/. .; "
# If you run this script inside a hacklet directory, we will execute the hacklet
$CMD+="[[ -f execute_permissions.sh ]] && ./execute_permissions.sh; "
# We will drop a root shell for you to experiment with
$CMD+="zsh; "

# Run Docker
docker run --rm -v "${PWD}:/mnt/host" -it $DIMG /bin/bash -c $CMD