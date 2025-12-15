
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example: Managing VM images in Harvester
#
# This example demonstrates how to create, list, and manage VM images.
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Example: Managing VM images in Harvester

This example demonstrates how to create, list, and manage VM images.
"""

from harvesterpy import HarvesterClient

# Initialize client
client = HarvesterClient(
    host='https://your-harvester-host/',
    token='replaceme-with-your-token',
)

# Create a new image from URL
image_spec = {
    'apiVersion': 'harvesterhci.io/v1beta1',
    'kind': 'VirtualMachineImage',
    'metadata': {
        'name': 'ubuntu-20.04',
        'namespace': 'default',
        'labels': {
            'os': 'ubuntu'
        }
    },
    'spec': {
        'displayName': 'Ubuntu 20.04 LTS',
        'url': 'https://cloud-images.ubuntu.com/releases/focal/release/ubuntu-20.04-server-cloudimg-amd64.img',
        'sourceType': 'download'
    }
}

print("Creating VM image...")
try:
    image = client.images.create(image_spec, namespace='default')
    print(f"Image created: {image['metadata']['name']}")
    print(f"Display name: {image['spec']['displayName']}")
except Exception as e:
    print(f"Error creating image: {e}")

# List all images
print("\nListing all images...")
images = client.images.list(namespace='default')
for image in images:
    name = image['metadata']['name']
    display_name = image['spec'].get('displayName', name)
    progress = image.get('status', {}).get('progress', 0)
    print(f"  - {name} ({display_name}) - Progress: {progress}%")

# Get specific image details
print("\nGetting image details...")
try:
    image = client.images.get('ubuntu-20.04', namespace='default')
    print(f"Image: {image['metadata']['name']}")
    print(f"Status: {image.get('status', {}).get('conditions', [])}")
except Exception as e:
    print(f"Error getting image: {e}")
