
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Network resource manager
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Network resource manager
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource


class Networks(BaseResource):
    """
    Manager for Network resources in Harvester.
    
    Provides methods to manage networks and network attachment definitions.
    """
    
    def __init__(self, client):
        super().__init__(client)
        self.base_path = "/apis/k8s.cni.cncf.io/v1/namespaces"
    
    def list(
        self,
        namespace: str = "default",
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all network attachment definitions in a namespace.
        
        Args:
            namespace: Namespace to list networks from (default: "default")
            params: Additional query parameters
        
        Returns:
            List of network objects
        """
        path = f"{self.base_path}/{namespace}/network-attachment-definitions"
        response = self.client.get(path, params=params)
        
        if isinstance(response, dict) and 'items' in response:
            return response['items']
        return response
    
    def get(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get a specific network attachment definition.
        
        Args:
            name: Network name
            namespace: Namespace (default: "default")
        
        Returns:
            Network object
        """
        path = f"{self.base_path}/{namespace}/network-attachment-definitions/{name}"
        return self.client.get(path)
    
    def create(
        self,
        data: Dict[str, Any],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a new network attachment definition.
        
        Args:
            data: Network specification data
            namespace: Namespace (default: "default")
        
        Returns:
            Created network object
        """
        path = f"{self.base_path}/{namespace}/network-attachment-definitions"
        return self.client.post(path, json=data)
    
    def update(
        self,
        name: str,
        data: Dict[str, Any],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Update a network attachment definition.
        
        Args:
            name: Network name
            data: Updated network specification
            namespace: Namespace (default: "default")
        
        Returns:
            Updated network object
        """
        path = f"{self.base_path}/{namespace}/network-attachment-definitions/{name}"
        return self.client.put(path, json=data)
    
    def delete(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a network attachment definition.
        
        Args:
            name: Network name
            namespace: Namespace (default: "default")
        
        Returns:
            Deletion response
        """
        path = f"{self.base_path}/{namespace}/network-attachment-definitions/{name}"
        return self.client.delete(path)
