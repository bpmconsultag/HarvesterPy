#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, bpmconsultag
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: harvester_image
short_description: Manage VM images in SUSE Harvester HCI
version_added: "0.1.5"
description:
    - Create, update, or delete VM images in SUSE Harvester HCI.
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
            - Name of the VM image
        required: true
        type: str
    namespace:
        description:
            - Namespace for the VM image
        required: false
        type: str
        default: "default"
    state:
        description:
            - Desired state of the image
        required: false
        type: str
        choices: ['present', 'absent']
        default: 'present'
    url:
        description:
            - URL to download the image from
        required: false
        type: str
    display_name:
        description:
            - Display name for the image
        required: false
        type: str
    description:
        description:
            - Description of the image
        required: false
        type: str
    source_type:
        description:
            - Source type for the image
        required: false
        type: str
        default: "download"
        choices: ['download', 'upload']
    storage_class:
        description:
            - Storage class for the image
        required: false
        type: str
    labels:
        description:
            - Labels to apply to the image
        required: false
        type: dict
requirements:
    - harvesterpy >= 0.1.5
author:
    - bpmconsultag
'''

EXAMPLES = r'''
# Create an image from URL
- name: Create VM image from URL
  harvester_image:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "ubuntu-20.04"
    namespace: "default"
    state: present
    url: "https://cloud-images.ubuntu.com/releases/focal/release/ubuntu-20.04-server-cloudimg-amd64.img"
    display_name: "Ubuntu 20.04 LTS"
    description: "Ubuntu 20.04 cloud image"

# Delete an image
- name: Delete VM image
  harvester_image:
    host: "https://harvester.example.com"
    token: "your-api-token"
    name: "ubuntu-20.04"
    namespace: "default"
    state: absent
'''

RETURN = r'''
image:
    description: VM image object
    returned: success
    type: dict
    sample: {
        "metadata": {
            "name": "ubuntu-20.04",
            "namespace": "default"
        },
        "spec": {
            "url": "https://cloud-images.ubuntu.com/...",
            "displayName": "Ubuntu 20.04 LTS"
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


def build_image_spec(module_params):
    """Build image specification from module parameters"""
    name = module_params['name']
    namespace = module_params['namespace']
    
    spec = {
        'displayName': module_params.get('display_name', name),
        'sourceType': module_params.get('source_type', 'download'),
    }
    
    if module_params.get('url'):
        spec['url'] = module_params['url']
    
    if module_params.get('description'):
        spec['description'] = module_params['description']
    
    if module_params.get('storage_class'):
        spec['storageClassName'] = module_params['storage_class']
    
    image_spec = {
        'apiVersion': 'harvesterhci.io/v1beta1',
        'kind': 'VirtualMachineImage',
        'metadata': {
            'name': name,
            'namespace': namespace,
        },
        'spec': spec
    }
    
    if module_params.get('labels'):
        image_spec['metadata']['labels'] = module_params['labels']
    
    return image_spec


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
            url=dict(type='str', required=False),
            display_name=dict(type='str', required=False),
            description=dict(type='str', required=False),
            source_type=dict(type='str', required=False, default='download',
                           choices=['download', 'upload']),
            storage_class=dict(type='str', required=False),
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
        'image': {},
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
        
        # Check if image exists
        image_exists = False
        existing_image = None
        try:
            existing_image = client.images.get(name, namespace=namespace)
            image_exists = True
        except HarvesterNotFoundError:
            image_exists = False
        
        if state == 'absent':
            if image_exists:
                if not module.check_mode:
                    client.images.delete(name, namespace=namespace)
                result['changed'] = True
                result['message'] = f"Image '{name}' deleted"
            else:
                result['message'] = f"Image '{name}' does not exist"
        
        elif state == 'present':
            if not image_exists:
                if not module.params.get('url'):
                    module.fail_json(msg="'url' is required when creating a new image")
                
                image_spec = build_image_spec(module.params)
                if not module.check_mode:
                    result['image'] = client.images.create(image_spec, namespace=namespace)
                result['changed'] = True
                result['message'] = f"Image '{name}' created"
            else:
                result['image'] = existing_image
                result['message'] = f"Image '{name}' already exists"
        
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
