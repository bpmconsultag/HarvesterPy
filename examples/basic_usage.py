#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Basic usage example for HarvesterPy
# 
# This example demonstrates how to connect to Harvester and perform
# basic operations on virtual machines.
# 
# 
# Copyright: (c) 2024, bpmconsultag
# MIT License

from harvesterpy import HarvesterClient

# Initialize client with token authentication
client = HarvesterClient(
    host='https://harvester.example.com',
    token='replaceme-with-your-token',
    verify_ssl=True  # Set to False for self-signed certificates
)

# List all virtual machines in the default namespace
print("Listing all virtual machines...")
vms = client.virtual_machines.list(namespace='default')
for vm in vms:
    vm_name = vm['metadata']['name']
    print(f"  - {vm_name}")

# Get details of a specific VM
if vms:
    vm_name = vms[0]['metadata']['name']
    print(f"\nGetting details for VM: {vm_name}")
    vm = client.virtual_machines.get(vm_name, namespace='default')
    print(f"  Status: {vm.get('status', {}).get('printableStatus', 'Unknown')}")

# List all images
print("\nListing all VM images...")
images = client.images.list(namespace='default')
for image in images:
    image_name = image['metadata']['name']
    display_name = image['spec'].get('displayName', image_name)
    print(f"  - {image_name} ({display_name})")

# List all nodes
print("\nListing all cluster nodes...")
nodes = client.nodes.list()
for node in nodes:
    node_name = node['metadata']['name']
    status = 'Ready' if any(
        c['type'] == 'Ready' and c['status'] == 'True'
        for c in node['status'].get('conditions', [])
    ) else 'NotReady'
    print(f"  - {node_name}: {status}")
