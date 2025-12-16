#!/bin/bash

set -e -x
set -a
source examples/.env
set +a

ansible-playbook -v -i examples/inventory.ini examples/create_vm.yml --module-path=library -e "harvester_verify_ssl=false"