#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, bpmconsultag
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: harvester_network
short_description: Manage networks in SUSE Harvester HCI
version_added: "0.1.5"
description:
    - Create, update, or delete network attachment definitions in SUSE Harvester HCI.
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
            - Name of the network
        required: true
        type: str
    namespace:
        description:
            - Namespace for the network
        required: false
        type: str
        default: "default"
    state:
        description:
            - Desired state of the network
        required: false
        type: str
        choices: ['present', 'absent']
        default: 'present'
    config:
        description:
            - Network configuration JSON string or dict
        required: false
        type: raw
    labels:
        description:
            - Labels to apply to the network
        required: false
        type: dict
requirements:
    - harvesterpy >= 0.1.5
author:
    - bpmconsultag
'''

EXAMPLES = r'''
# Create a network
- name: Create network attachment definition
  harvester_network:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-network"
    namespace: "default"
    state: present
    config:
      cniVersion: "0.3.1"
      type: "bridge"
      bridge: "br0"

# Delete a network
- name: Delete network attachment definition
  harvester_network:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-network"
    namespace: "default"
    state: absent
'''

RETURN = r'''
network:
    description: Network object
    returned: success
    type: dict
    sample: {
        "metadata": {
            "name": "my-network",
            "namespace": "default"
        },
        "spec": {
            "config": "{\"cniVersion\":\"0.3.1\",\"type\":\"bridge\"}"
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

from ansible.module_utils.basic import AnsibleModule
import json

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


def build_network_spec(module_params):
    """Build network specification from module parameters"""
    name = module_params['name']
    namespace = module_params['namespace']
    config = module_params.get('config', {})
    
    # Convert config to JSON string if it's a dict
    if isinstance(config, dict):
        config_str = json.dumps(config)
    else:
        config_str = config
    
    network_spec = {
        'apiVersion': 'k8s.cni.cncf.io/v1',
        'kind': 'NetworkAttachmentDefinition',
        'metadata': {
            'name': name,
            'namespace': namespace,
        },
        'spec': {
            'config': config_str
        }
    }
    
    if module_params.get('labels'):
        network_spec['metadata']['labels'] = module_params['labels']
    
    return network_spec


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
            state=dict(type='str', required=False, default='present',
                      choices=['present', 'absent']),
            config=dict(type='raw', required=False),
            labels=dict(type='dict', required=False),
        ),
        required_one_of=[
            ['token', 'username']
        ],
        required_together=[
            ['username', 'password']
        ],
        supports_check_mode=True,
    )
    
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
    
    result = {
        'changed': False,
        'network': {},
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
        
        # Check if network exists
        network_exists = False
        existing_network = None
        try:
            existing_network = client.networks.get(name, namespace=namespace)
            network_exists = True
        except HarvesterNotFoundError:
            network_exists = False
        
        if state == 'absent':
            if network_exists:
                if not module.check_mode:
                    client.networks.delete(name, namespace=namespace)
                result['changed'] = True
                result['message'] = f"Network '{name}' deleted"
            else:
                result['message'] = f"Network '{name}' does not exist"
        
        elif state == 'present':
            if not network_exists:
                if not module.params.get('config'):
                    module.fail_json(msg="'config' is required when creating a new network")
                
                network_spec = build_network_spec(module.params)
                if not module.check_mode:
                    result['network'] = client.networks.create(network_spec, namespace=namespace)
                result['changed'] = True
                result['message'] = f"Network '{name}' created"
            else:
                result['network'] = existing_network
                result['message'] = f"Network '{name}' already exists"
        
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
