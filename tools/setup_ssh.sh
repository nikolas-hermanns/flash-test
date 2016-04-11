#!/bin/bash
usage() {
    echo "usage: $0 [-v] -d <destination> -i <installer_type> -a <installer_ip>" >&2
    echo "[-v] Virtualized deployment" >&2
}

verify_connectivity() {
    local ip=$1
    info "Verifying connectivity to $ip..."
    for i in $(seq 0 10); do
        if ping -c 1 -W 1 $ip > /dev/null; then
            info "$ip is reachable!"
            return 0
        fi
        sleep 1
    done
    error "Can not talk to $ip."
}

#Get options
while getopts ":i:a:h:v" optchar; do
    case "${optchar}" in
        i) installer_type=${OPTARG} ;;
        a) installer_ip=${OPTARG} ;;
        *) echo "Non-option argument: '-${OPTARG}'" >&2
           usage
           exit 2
           ;;
    esac
done

# set vars from env if not provided by user as options
installer_type=${installer_type:-$INSTALLER_TYPE}
installer_ip=${installer_ip:-$INSTALLER_IP}

if [ -z $installer_type ] || [ -z $installer_ip ]; then
    usage
    exit 2
fi

function gen_flash_test_conf(){
  echo "
env:
  cloud_deployer: $installer_type
  hypervisor_ssh_user: root
  nodes:
    main_controller:
      address: $controller_ip
      user: root
  test_vm:
    user: cirros
    password: 'cubswin:)'
" >> /etc/flash_test.yaml
}
ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

if [ "$installer_type" == "fuel" ]; then
    verify_connectivity $installer_ip
    $SSH_FUEL="sshpass -p r00tme ssh 2>/dev/null $ssh_options root@${installer_ip}"
    $SCP_FUEL="sshpass -p r00tme scp 2>/dev/null $ssh_options root@${installer_ip}"
    # Check if controller is alive (online='True')
    controller_ip=$(SSH_FUEL \
        'fuel node | grep controller | grep True | awk "{print \$10}" | tail -1') &> /dev/null

    if [ -z $controller_ip ]; then
        error "The controller $controller_ip is not up. Please check that the POD is correctly deployed."
    fi
    gen_flash_test_conf

    mkdir -p ~/.flash_test/
    $SCP_FUEL:./.ssh/id_rsa* ~/.flash_test/
fi
