
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Volume resource manager
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Volume resource manager
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource


class Volumes(BaseResource):
    """
    Manager for Volume resources in Harvester.
    
    Provides methods to manage persistent volumes.
    """
    
    def __init__(self, client):
        super().__init__(client)
        self.base_path = "/api/v1/namespaces"
    
    def list(
        self,
        namespace: str = "default",
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all volumes in a namespace.
        
        Args:
            namespace: Namespace to list volumes from (default: "default")
            params: Additional query parameters
        
        Returns:
            List of volume objects
        """
        path = f"{self.base_path}/{namespace}/persistentvolumeclaims"
        print( path )
        response = self.client.get(path, params=params)
        
        if isinstance(response, dict) and 'items' in response:
            return response['items']
        return response
    
    def get(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get a specific volume.
        
        Args:
            name: Volume name
            namespace: Namespace (default: "default")
        
        Returns:
            Volume object
        """
        path = f"{self.base_path}/{namespace}/persistentvolumeclaims/{name}"
        return self.client.get(path)
    
    def create(
        self,
        data: Dict[str, Any],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a new volume.
        
        Args:
            data: Volume specification data
            namespace: Namespace (default: "default")
        
        Returns:
            Created volume object
        """
        
        path = f"{self.base_path}/{namespace}/persistentvolumeclaims"
        print(f"Creating volume at path: {path}")
        return self.client.post(path, json=data)
    
    def update(
        self,
        name: str,
        data: Dict[str, Any],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Update a volume.
        
        Args:
            name: Volume name
            data: Updated volume specification
            namespace: Namespace (default: "default")
        
        Returns:
            Updated volume object
        """
        path = f"{self.base_path}/{namespace}/persistentvolumeclaims/{name}"
        return self.client.put(path, json=data)
    
    def delete(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a volume.
        
        Args:
            name: Volume name
            namespace: Namespace (default: "default")
        
        Returns:
            Deletion response
        """
        path = f"{self.base_path}/{namespace}/persistentvolumeclaims/{name}"
        return self.client.delete(path)
