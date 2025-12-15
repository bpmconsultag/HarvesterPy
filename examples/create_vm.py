
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example: Creating a virtual machine in Harvester
#
# This example demonstrates how to create a new virtual machine.
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Example: Creating a virtual machine in Harvester

This example demonstrates how to create a new virtual machine.
"""

from harvesterpy import HarvesterClient
import sys

# Initialize client
client = HarvesterClient(
    host='https://your-harvester-host/',
    token='replaceme-with-your-token',
)

image_spec = {
    'apiVersion': 'harvesterhci.io/v1beta1',
    'kind': 'VirtualMachineImage',
    'metadata': {
        'name': 'ubuntu-20.04-oci',
        'namespace': 'default',
        'labels': {
            'os': 'ubuntu'
        }
    },
    'spec': {
        'displayName': 'Ubuntu 20.04 LTS',
        'url': 'oci://harbor.intra.bpm.ch/vm-images/ubuntu:latest',
        'sourceType': 'download'
    }
}

# Create the image
print("Creating VM image...")
try:
     image = client.images.create(image_spec, namespace='default')
     print(f"Image created: {image['metadata']['name']}")
except Exception as e:
    print(f"Error creating image: {e}")
    #sys.exit(1)

# Create a volume for the VM
volume_spec = {
    'type': 'persistentvolumeclaim',
    'metadata': {
        'namespace': 'default',
        'annotations': {
            'harvesterhci.io/imageId': 'default/ubuntu-20.04'
        },
        'labels': {},
        'name': 'my-ubuntu-volume'
    },
    '__clone': True,
    'spec': {
        'accessModes': ['ReadWriteMany'],
        'storageClassName': 'longhorn-ubuntu-20.04',
        'volumeName': '',
        'resources': {
            'requests': {
                'storage': '3Gi'
            }
        },
        'volumeMode': 'Block'
    }
}

# Create the volume
print("Creating volume for VM...")
try:
    volume = client.volumes.create(volume_spec, namespace='default')
    print(f"Volume created: {volume['metadata']['name']}")
except Exception as e:
    print(f"Error creating volume: {e}")
    sys.exit(1)
# Define VM specification
vm_spec = {
    'apiVersion': 'kubevirt.io/v1',
    'kind': 'VirtualMachine',
    'metadata': {
        'name': 'my-ubuntu-vm3',
        'namespace': 'default',
        'labels': {
            'app': 'web-server'
        }
    },
    'spec': {
        'running': True,
        'template': {
            'metadata': {
                'labels': {
                    'kubevirt.io/vm': 'my-ubuntu-vm'
                }
            },
            'spec': {
                'domain': {
                    'cpu': {
                        'cores': 2
                    },
                    'memory': {
                        'guest': '4Gi'
                    },
                    'devices': {
                        'disks': [
                            {
                                'name': 'disk0',
                                'disk': {
                                    'bus': 'virtio'
                                }
                            }
                        ],
                        'interfaces': [
                            {
                                'name': 'default',
                                'masquerade': {}
                            }
                        ]
                    }
                },
                'networks': [
                    {
                        'name': 'default',
                        'pod': {}
                    }
                ],
                'volumes': [
                    {
                        'name': 'disk0',
                        'persistentVolumeClaim': {
                            'claimName': 'my-ubuntu-volume'
                        }
                    }
                ]
            }
        }
    }
}

# Create the VM
print("Creating virtual machine...")
try:
    vm = client.virtual_machines.create(vm_spec, namespace='default')
    print(f"VM created successfully: {vm['metadata']['name']}")
    print(f"Status: {vm.get('status', {}).get('printableStatus', 'Creating')}")
except Exception as e:
    print(f"Error creating VM: {e}")
