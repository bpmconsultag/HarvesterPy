#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, bpmconsultag
# MIT License
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: harvester_vm
short_description: Manage virtual machines in SUSE Harvester HCI
version_added: "0.1.5"
description:
    - Create, update, start, stop, restart, or delete virtual machines in SUSE Harvester HCI.
    - This module uses the harvesterpy Python library.
options:
    host:
        description:
            - Harvester host URL (e.g., 'https://harvester.example.com')
        required: true
        type: str
    token:
        description:
            - API token for authentication
        required: false
        type: str
    username:
        description:
            - Username for basic authentication
        required: false
        type: str
    password:
        description:
            - Password for basic authentication
        required: false
        type: str
    verify_ssl:
        description:
            - Whether to verify SSL certificates
        required: false
        type: bool
        default: true
    timeout:
        description:
            - Request timeout in seconds
        required: false
        type: int
        default: 30
    name:
        description:
            - Name of the virtual machine
        required: true
        type: str
    namespace:
        description:
            - Namespace for the virtual machine
        required: false
        type: str
        default: "default"
    state:
        description:
            - Desired state of the virtual machine
        required: false
        type: str
        choices: ['present', 'absent', 'started', 'stopped', 'restarted']
        default: 'present'
    running:
        description:
            - Whether the VM should be running after creation
        required: false
        type: bool
        default: true
    cpu_cores:
        description:
            - Number of CPU cores
        required: false
        type: int
        default: 2
    memory:
        description:
            - Memory allocation (e.g., '4Gi', '2048Mi')
        required: false
        type: str
        default: "4Gi"
    disks:
        description:
            - List of disk configurations
        required: false
        type: list
        elements: dict
    networks:
        description:
            - List of network configurations
        required: false
        type: list
        elements: dict
    labels:
        description:
            - Labels to apply to the VM
        required: false
        type: dict
    spec:
        description:
            - Complete VM specification (advanced usage)
        required: false
        type: dict
    cloud_init:
        description:
            - Cloud-init configuration for the VM
            - If not provided, no cloud-init will be configured
        required: false
        type: dict
        suboptions:
            user_data:
                description:
                    - Cloud-init user data (will be converted to YAML)
                required: false
                type: dict
            user_data_raw:
                description:
                    - Raw cloud-init user data string (takes precedence over user_data)
                required: false
                type: str
            network_data:
                description:
                    - Cloud-init network data
                required: false
                type: dict
requirements:
    - harvesterpy >= 0.1.5
author:
    - bpmconsultag
'''

EXAMPLES = r'''
# Create a simple VM
- name: Create a virtual machine
  harvester_vm:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-vm"
    namespace: "default"
    state: present
    cpu_cores: 2
    memory: "4Gi"
    disks:
      - name: disk0
        volume_name: my-volume
        bus: virtio

# Start a VM
- name: Start a virtual machine
  harvester_vm:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-vm"
    namespace: "default"
    state: started

# Stop a VM
- name: Stop a virtual machine
  harvester_vm:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-vm"
    namespace: "default"
    state: stopped

# Delete a VM
- name: Delete a virtual machine
  harvester_vm:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-vm"
    namespace: "default"
    state: absent

# Create VM with custom spec
- name: Create VM with full specification
  harvester_vm:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-vm"
    namespace: "default"
    spec:
      running: true
      template:
        spec:
          domain:
            cpu:
              cores: 4
            memory:
              guest: "8Gi"
            devices:
              disks:
                - name: disk0
                  disk:
                    bus: virtio
              interfaces:
                - name: default
                  masquerade: {}
          networks:
            - name: default
              pod: {}
          volumes:
            - name: disk0
              persistentVolumeClaim:
                claimName: my-volume

# Create VM with cloud-init configuration
- name: Create VM with cloud-init
  harvester_vm:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-vm"
    namespace: "default"
    cpu_cores: 2
    memory: "4Gi"
    disks:
      - name: disk0
        volume_name: my-volume
        bus: virtio
    networks:
      - name: default
        multus:
          networkName: default/br-clients
    cloud_init:
      user_data:
        hostname: my-vm
        users:
          - name: ubuntu
            ssh_authorized_keys:
              - ssh-ed25519 AAAAC3... user@example.com
            sudo: ALL=(ALL) NOPASSWD:ALL
            shell: /bin/bash
        package_update: true
        packages:
          - qemu-guest-agent
        runcmd:
          - systemctl enable --now qemu-guest-agent
'''

RETURN = r'''
vm:
    description: Virtual machine object
    returned: success
    type: dict
    sample: {
        "metadata": {
            "name": "my-vm",
            "namespace": "default"
        },
        "spec": {
            "running": true
        }
    }
changed:
    description: Whether the resource was changed
    returned: always
    type: bool
message:
    description: Informational message about the operation
    returned: always
    type: str
'''

import pprint
import sys

from ansible.module_utils.basic import AnsibleModule

try:
    from harvesterpy import HarvesterClient
    from harvesterpy.exceptions import (
        HarvesterException,
        HarvesterAPIError,
        HarvesterAuthenticationError,
        HarvesterNotFoundError,
    )
    HAS_HARVESTERPY = True
except ImportError:
    HAS_HARVESTERPY = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def build_vm_spec(module_params, debug=False):
    """Build VM specification from module parameters"""
    name = module_params['name']
    namespace = module_params['namespace']
    
    # If custom spec provided, use it
    if module_params.get('spec'):
        vm_spec = {
            'apiVersion': 'kubevirt.io/v1',
            'kind': 'VirtualMachine',
            'metadata': {
                'name': name,
                'namespace': namespace,
            },
            'spec': module_params['spec']
        }
        if module_params.get('labels', {}):
            vm_spec['metadata']['labels'] = module_params['labels']
        return vm_spec
    
    # Build basic spec
    disks = module_params.get('disks', [])
    networks = module_params.get('networks', [])
    interfaces = module_params.get('interfaces', [])
    # Fail if no networks defined
    if not networks:
        raise ValueError("At least one network configuration must be provided in the 'networks' parameter")
    
    # Default disk configuration
    if not disks:
        disks = [{'name': 'disk0', 'bus': 'virtio'}]
    
    # Build disk devices and volumes
    disk_devices = []
    volumes = []
    for disk in disks:
        disk_name = disk.get('name', 'disk0')
        disk_devices.append({
            'name': disk_name,
            'disk': {
                'bus': disk.get('bus', 'virtio')
            }
        })
        if 'volume_name' in disk:
            volumes.append({
                'name': disk_name,
                'persistentVolumeClaim': {
                    'claimName': disk['volume_name']
                }
            })

    #
    
    # Add cloud-init disk if cloud_init configuration is provided
    cloud_init_config = module_params.get('cloud_init')
    if cloud_init_config:
        cloud_init_volume = {
            'name': 'cloudinitdisk',
            'cloudInitNoCloud': {}
        }
        
        # Handle user_data (raw takes precedence)
        if 'user_data_raw' in cloud_init_config:
            user_data_str = cloud_init_config['user_data_raw']
            # Ensure it starts with #cloud-config if not already present
            if not user_data_str.startswith('#cloud-config'):
                user_data_str = '#cloud-config\n' + user_data_str
            cloud_init_volume['cloudInitNoCloud']['userData'] = user_data_str
        elif 'user_data' in cloud_init_config:
            # Convert user_data dict to YAML string
            if not HAS_YAML:
                raise ImportError('PyYAML is required for cloud-init userData YAML conversion. Please install it with pip install PyYAML')
            user_data_str = '#cloud-config\n' + yaml.dump(
                cloud_init_config['user_data'], 
                default_flow_style=False,
                sort_keys=False
            )
            cloud_init_volume['cloudInitNoCloud']['userData'] = user_data_str
        
        # Handle network_data if provided
        if 'network_data' in cloud_init_config:
            if not HAS_YAML:
                raise ImportError('PyYAML is required for cloud-init networkData YAML conversion. Please install it with pip install PyYAML')
            network_data_str = yaml.dump(
                cloud_init_config['network_data'],
                default_flow_style=False,
                sort_keys=False
            )
            cloud_init_volume['cloudInitNoCloud']['networkData'] = network_data_str
        
        # Only add cloud-init disk if we have any data
        if 'userData' in cloud_init_volume['cloudInitNoCloud'] or 'networkData' in cloud_init_volume['cloudInitNoCloud']:
            volumes.append(cloud_init_volume)
            disk_devices.append({
                'name': 'cloudinitdisk',
                'disk': {
                    'bus': 'virtio'
                }
            })

    vm_spec = {
        'apiVersion': 'kubevirt.io/v1',
        'kind': 'VirtualMachine',
        'metadata': {
            'name': name,
            'namespace': namespace,
        },
        'spec': {
            'running': module_params.get('running', True),
            'template': {
                'metadata': {
                    'annotations': {
                        # To be implemented: SSH key injection
                        'harvesterhci.io/sshNames': '[]'
                    },
                    'labels': module_params.get('labels', {})
                },
                'spec': {
                    'domain': {
                        'cpu': {
                            'cores': module_params.get('cpu_cores', 2)
                        },
                        'memory': {
                            'guest': module_params.get('memory', '4Gi')
                        },
                        'devices': {
                            'disks': disk_devices,
                            'interfaces': interfaces
                        },
                        'features': {
                            'acpi': {
                                'enabled': True
                            }
                        },
                        'machine': {
                            'type': 'q35'
                        },
                        'resources': {
                            'requests': {
                                'cpu': str(module_params.get('cpu_cores', 2)),
                                'memory': module_params.get('memory', '4Gi'),
                            },
                            'limits': {
                                'cpu': str(module_params.get('cpu_cores', 2)),
                                'memory': module_params.get('memory', '4Gi'),
                            }
                        }
                    },
                    'networks': networks,
                    'volumes': volumes
                }
            }
        }
    }

    return vm_spec

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            token=dict(type='str', required=False, no_log=True),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            verify_ssl=dict(type='bool', required=False, default=True),
            timeout=dict(type='int', required=False, default=30),
            name=dict(type='str', required=True),
            namespace=dict(type='str', required=False, default='default'),
            state=dict(type='str', required=False, default='present', choices=['present', 'absent', 'started', 'stopped', 'restarted']),
            running=dict(type='bool', required=False, default=True),
            cpu_cores=dict(type='int', required=False, default=2),
            memory=dict(type='str', required=False, default='4Gi'),
            disks=dict(type='list', elements='dict', required=False),
            networks=dict(type='list', elements='dict', required=False),
            interfaces=dict(type='list', elements='dict', required=False),
            labels=dict(type='dict', required=False, default=None),
            spec=dict(type='dict', required=False),
            cloud_init=dict(type='dict', required=False, default=None),
            debug=dict(type='bool', required=False, default=False),
        ),
        required_one_of=[
            ['token', 'username']
        ],
        required_together=[
            ['username', 'password']
        ],
        supports_check_mode=True,
    )
    # Ensure labels is always a dict
    if module.params.get('labels') is None:
        module.params['labels'] = {}

    if not HAS_HARVESTERPY:
        module.fail_json(msg='harvesterpy Python library is required. Install with: pip install harvesterpy')

    # Get parameters
    host = module.params['host']
    token = module.params.get('token')
    username = module.params.get('username')
    password = module.params.get('password')
    verify_ssl = module.params['verify_ssl']
    timeout = module.params['timeout']
    name = module.params['name']
    namespace = module.params['namespace']
    state = module.params['state']
    debug = module.params.get('debug', False)

    result = {
        'changed': False,
        'vm': {},
        'message': ''
    }

    try:
        # Initialize Harvester client
        client = HarvesterClient(
            host=host,
            token=token,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            timeout=timeout
        )

        # Check if VM exists
        vm_exists = False
        existing_vm = None
        try:
            existing_vm = client.virtual_machines.get(name, namespace=namespace)
            vm_exists = True
        except HarvesterNotFoundError:
            vm_exists = False

        if state == 'absent':
            if vm_exists:
                if not module.check_mode:
                    client.virtual_machines.delete(name, namespace=namespace)
                result['changed'] = True
                result['message'] = f"VM '{name}' deleted"
            else:
                result['message'] = f"VM '{name}' does not exist"

        elif state == 'present':
            if not vm_exists:
                vm_spec = build_vm_spec(module.params, debug=debug)
                if debug:
                    sys.stderr.write("[DEBUG] vm_spec:\n" + pprint.pformat(vm_spec) + "\n")
                if not module.check_mode:
                    result['vm'] = client.virtual_machines.create(vm_spec, namespace=namespace)
                result['changed'] = True
                result['message'] = f"VM '{name}' created"
            else:
                result['vm'] = existing_vm
                result['message'] = f"VM '{name}' already exists"

        elif state == 'started':
            if not vm_exists:
                module.fail_json(msg=f"VM '{name}' does not exist")
            # Check if VM is already running
            vm_running = existing_vm.get('spec', {}).get('running', False)
            if not vm_running:
                if not module.check_mode:
                    result['vm'] = client.virtual_machines.start(name, namespace=namespace)
                result['changed'] = True
                result['message'] = f"VM '{name}' started"
            else:
                result['vm'] = existing_vm
                result['message'] = f"VM '{name}' is already running"

        elif state == 'stopped':
            if not vm_exists:
                module.fail_json(msg=f"VM '{name}' does not exist")
            # Check if VM is already stopped
            vm_running = existing_vm.get('spec', {}).get('running', False)
            if vm_running:
                if not module.check_mode:
                    result['vm'] = client.virtual_machines.stop(name, namespace=namespace)
                result['changed'] = True
                result['message'] = f"VM '{name}' stopped"
            else:
                result['vm'] = existing_vm
                result['message'] = f"VM '{name}' is already stopped"

        elif state == 'restarted':
            if not vm_exists:
                module.fail_json(msg=f"VM '{name}' does not exist")
            # Restart always triggers a change
            if not module.check_mode:
                result['vm'] = client.virtual_machines.restart(name, namespace=namespace)
            result['changed'] = True
            result['message'] = f"VM '{name}' restarted"

        module.exit_json(**result)

    except HarvesterAuthenticationError as e:
        module.fail_json(msg=f"Authentication failed: {str(e)}")
    except HarvesterAPIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except HarvesterException as e:
        module.fail_json(msg=f"Harvester error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}")


if __name__ == '__main__':
    main()
