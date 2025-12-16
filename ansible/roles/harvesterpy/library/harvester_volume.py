#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, bpmconsultag
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: harvester_volume
short_description: Manage volumes in SUSE Harvester HCI
version_added: "0.1.5"
description:
    - Create, update, or delete persistent volumes in SUSE Harvester HCI.
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
            - Name of the volume
        required: true
        type: str
    namespace:
        description:
            - Namespace for the volume
        required: false
        type: str
        default: "default"
    state:
        description:
            - Desired state of the volume
        required: false
        type: str
        choices: ['present', 'absent']
        default: 'present'
    storage:
        description:
            - Storage size (e.g., '10Gi', '100Mi')
        required: false
        type: str
        default: "10Gi"
    access_modes:
        description:
            - Access modes for the volume
        required: false
        type: list
        elements: str
        default: ['ReadWriteOnce']
    storage_class:
        description:
            - Storage class for the volume
        required: false
        type: str
    volume_mode:
        description:
            - Volume mode
        required: false
        type: str
        choices: ['Filesystem', 'Block']
        default: 'Filesystem'
    labels:
        description:
            - Labels to apply to the volume
        required: false
        type: dict
requirements:
    - harvesterpy >= 0.1.5
author:
    - bpmconsultag
'''

EXAMPLES = r'''
# Create a volume
- name: Create persistent volume
  harvester_volume:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-volume"
    namespace: "default"
    state: present
    storage: "10Gi"
    access_modes:
      - ReadWriteOnce

# Delete a volume
- name: Delete persistent volume
  harvester_volume:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "my-volume"
    namespace: "default"
    state: absent
'''

RETURN = r'''
volume:
    description: Volume object
    returned: success
    type: dict
    sample: {
        "metadata": {
            "name": "my-volume",
            "namespace": "default"
        },
        "spec": {
            "accessModes": ["ReadWriteOnce"],
            "resources": {
                "requests": {
                    "storage": "10Gi"
                }
            }
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


def build_volume_spec(module_params, module=None):
    """Build volume specification from module parameters"""
    name = module_params['name']
    namespace = module_params['namespace']

    spec = {
        'accessModes': module_params.get('access_modes', ['ReadWriteOnce']),
        'resources': {
            'requests': {
                'storage': module_params.get('storage', '10Gi')
            }
        },
        'volumeMode': module_params.get('volume_mode', 'Filesystem')
    }

    if module_params.get('storage_class'):
        spec['storageClassName'] = module_params['storage_class']

    volume_spec = {
        'type': 'persistentvolumeclaim',
        'apiVersion': 'v1',
        'kind': 'PersistentVolumeClaim',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': module_params.get('labels', {}),
        },
        'spec': spec
    }

    # Add volumeName if provided, else set to empty string
    if module_params.get('volume_name') is not None:
        volume_spec['spec']['volumeName'] = module_params['volume_name']
    else:
        volume_spec['spec']['volumeName'] = ''

    # Add image reference if provided
    if module_params.get('image'):
        # Add annotation for imageId
        image_name = module_params['image']
        if 'annotations' not in volume_spec['metadata']:
            volume_spec['metadata']['annotations'] = {}
        volume_spec['metadata']['annotations']['harvesterhci.io/imageId'] = f"{namespace}/{image_name}"
        # Set clone flag
        volume_spec['__clone'] = True

    return volume_spec


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
            storage=dict(type='str', required=False, default='10Gi'),
            access_modes=dict(type='list', elements='str', required=False,
                            default=['ReadWriteOnce']),
            storage_class=dict(type='str', required=False),
            volume_mode=dict(type='str', required=False, default='Filesystem',
                           choices=['Filesystem', 'Block']),
            labels=dict(type='dict', required=False),
            image=dict(type='str', required=False),
            volume_name=dict(type='str', required=False),
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
        'volume': {},
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
        
        # Check if volume exists
        volume_exists = False
        existing_volume = None
        try:
            existing_volume = client.volumes.get(name, namespace=namespace)
            volume_exists = True
        except HarvesterNotFoundError:
            volume_exists = False
        
        if state == 'absent':
            if volume_exists:
                if not module.check_mode:
                    client.volumes.delete(name, namespace=namespace)
                result['changed'] = True
                result['message'] = f"Volume '{name}' deleted"
            else:
                result['message'] = f"Volume '{name}' does not exist"
        
        elif state == 'present':
            if not volume_exists:
                volume_spec = build_volume_spec(module.params, module)
                if not module.check_mode:
                    result['volume'] = client.volumes.create(volume_spec, namespace=namespace)
                result['changed'] = True
                result['message'] = f"Volume '{name}' created"
            else:
                result['volume'] = existing_volume
                result['message'] = f"Volume '{name}' already exists"
        
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
