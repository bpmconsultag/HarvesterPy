
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Virtual Machine resource manager
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Virtual Machine resource manager
"""

from typing import Optional, Dict, Any
from .base import BaseResource


class VirtualMachines(BaseResource):
    """
    Manager for Virtual Machine resources in Harvester.
    
    Provides methods to manage VMs including creation, listing, updating,
    starting, stopping, and deletion.
    """
    
    def __init__(self, client):
        super().__init__(client)
        self.base_path = "/apis/kubevirt.io/v1/namespaces"
    
    def list(
        self,
        namespace: str = "default",
        params: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        List all virtual machines in a namespace.
        
        Args:
            namespace: Namespace to list VMs from (default: "default")
            params: Additional query parameters
        
        Returns:
            List of VM objects
        """
        path = f"{self.base_path}/{namespace}/virtualmachines"
        response = self.client.get(path, params=params)
        
        if isinstance(response, dict) and 'items' in response:
            return response['items']
        return response
    
    def get(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get a specific virtual machine.
        
        Args:
            name: VM name
            namespace: Namespace (default: "default")
        
        Returns:
            VM object
        """
        path = f"{self.base_path}/{namespace}/virtualmachines/{name}"
        return self.client.get(path)
    
    def create(
        self,
        data: Dict[str, Any],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a new virtual machine.
        
        Args:
            data: VM specification data
            namespace: Namespace (default: "default")
        
        Returns:
            Created VM object
        """
        path = f"{self.base_path}/{namespace}/virtualmachines"
        return self.client.post(path, json=data)
    
    def update(
        self,
        name: str,
        data: Dict[str, Any],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Update a virtual machine.
        
        Args:
            name: VM name
            data: Updated VM specification
            namespace: Namespace (default: "default")
        
        Returns:
            Updated VM object
        """
        path = f"{self.base_path}/{namespace}/virtualmachines/{name}"
        return self.client.put(path, json=data)
    
    def delete(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a virtual machine.
        
        Args:
            name: VM name
            namespace: Namespace (default: "default")
        
        Returns:
            Deletion response
        """
        path = f"{self.base_path}/{namespace}/virtualmachines/{name}"
        return self.client.delete(path)
    
    def start(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Start a virtual machine.
        
        Args:
            name: VM name
            namespace: Namespace (default: "default")
        
        Returns:
            Response from start operation
        """
        path = f"{self.base_path}/{namespace}/virtualmachines/{name}/start"
        return self.client.put(path)
    
    def stop(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Stop a virtual machine.
        
        Args:
            name: VM name
            namespace: Namespace (default: "default")
        
        Returns:
            Response from stop operation
        """
        path = f"{self.base_path}/{namespace}/virtualmachines/{name}/stop"
        return self.client.put(path)
    
    def restart(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Restart a virtual machine.
        
        Args:
            name: VM name
            namespace: Namespace (default: "default")
        
        Returns:
            Response from restart operation
        """
        path = f"{self.base_path}/{namespace}/virtualmachines/{name}/restart"
        return self.client.put(path)
