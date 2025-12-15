
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example: Error handling with HarvesterPy
#
# This example demonstrates how to handle different types of errors.
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Example: Error handling with HarvesterPy

This example demonstrates how to handle different types of errors.
"""

from harvesterpy import (
    HarvesterClient,
    HarvesterAuthenticationError,
    HarvesterConnectionError,
    HarvesterNotFoundError,
    HarvesterAPIError,
    HarvesterException
)

# Example 1: Handling authentication errors
print("Example 1: Authentication error")
try:
    client = HarvesterClient(
        host='https://harvester.example.com',
        token='invalid-token'
    )
    vms = client.virtual_machines.list()
except HarvesterAuthenticationError as e:
    print(f"  Authentication failed: {e}")
except HarvesterException as e:
    print(f"  Other error: {e}")

# Example 2: Handling connection errors
print("\nExample 2: Connection error")
try:
    client = HarvesterClient(
        host='https://nonexistent.example.com',
        token='some-token'
    )
    vms = client.virtual_machines.list()
except HarvesterConnectionError as e:
    print(f"  Connection failed: {e}")
except HarvesterException as e:
    print(f"  Other error: {e}")

# Example 3: Handling resource not found
print("\nExample 3: Resource not found")
try:
    client = HarvesterClient(
        host='https://harvester.example.com',
        token='your-api-token'
    )
    vm = client.virtual_machines.get('nonexistent-vm', namespace='default')
except HarvesterNotFoundError as e:
    print(f"  Resource not found: {e}")
    print(f"  Status code: {e.status_code}")
except HarvesterException as e:
    print(f"  Other error: {e}")

# Example 4: Handling general API errors
print("\nExample 4: API error")
try:
    client = HarvesterClient(
        host='https://harvester.example.com',
        token='your-api-token'
    )
    # Try to create an invalid resource
    invalid_spec = {'invalid': 'data'}
    vm = client.virtual_machines.create(invalid_spec, namespace='default')
except HarvesterAPIError as e:
    print(f"  API error: {e}")
    print(f"  Status code: {e.status_code}")
except HarvesterException as e:
    print(f"  Other error: {e}")

# Example 5: Comprehensive error handling
print("\nExample 5: Comprehensive error handling")
try:
    client = HarvesterClient(
        host='https://harvester.example.com',
        token='your-api-token'
    )
    
    # Try multiple operations
    vms = client.virtual_machines.list(namespace='default')
    print(f"  Found {len(vms)} VMs")
    
    images = client.images.list(namespace='default')
    print(f"  Found {len(images)} images")
    
except HarvesterAuthenticationError:
    print("  Please check your credentials")
except HarvesterConnectionError:
    print("  Please check your network connection and host URL")
except HarvesterNotFoundError:
    print("  The requested resource was not found")
except HarvesterAPIError as e:
    print(f"  API error occurred: {e}")
except Exception as e:
    print(f"  Unexpected error: {e}")
