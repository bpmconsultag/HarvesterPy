
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Base resource class for all Harvester resources
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Base resource class for all Harvester resources
"""

from typing import Optional, Dict, Any, List


class BaseResource:
    """
    Base class for all Harvester resource managers.
    
    Provides common methods for CRUD operations on resources.
    """
    
    def __init__(self, client):
        """
        Initialize the resource manager.
        
        Args:
            client: HarvesterClient instance
        """
        self.client = client
        self.base_path = None  # Should be overridden in subclasses
    
    def list(
        self,
        namespace: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all resources of this type.
        
        Args:
            namespace: Optional namespace to filter resources
            params: Additional query parameters
        
        Returns:
            List of resource objects
        """
        if namespace:
            path = f"{self.base_path}/{namespace}"
        else:
            path = self.base_path
        
        response = self.client.get(path, params=params)
        
        # Handle different response formats
        if isinstance(response, dict):
            # If response has 'data' or 'items' field, return that
            if 'data' in response and isinstance(response['data'], list):
                return response['data']
            elif 'items' in response and isinstance(response['items'], list):
                return response['items']
            # Otherwise return as single-item list
            return [response]
        elif isinstance(response, list):
            return response
        else:
            return []
    
    def get(self, name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a specific resource by name.
        
        Args:
            name: Resource name
            namespace: Optional namespace
        
        Returns:
            Resource object
        """
        if namespace:
            path = f"{self.base_path}/{namespace}/{name}"
        else:
            path = f"{self.base_path}/{name}"
        
        return self.client.get(path)
    
    def create(
        self,
        data: Dict[str, Any],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new resource.
        
        Args:
            data: Resource data
            namespace: Optional namespace
        
        Returns:
            Created resource object
        """
        if namespace:
            path = f"{self.base_path}/{namespace}"
        else:
            path = self.base_path
        
        return self.client.post(path, json=data)
    
    def update(
        self,
        name: str,
        data: Dict[str, Any],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing resource.
        
        Args:
            name: Resource name
            data: Updated resource data
            namespace: Optional namespace
        
        Returns:
            Updated resource object
        """
        if namespace:
            path = f"{self.base_path}/{namespace}/{name}"
        else:
            path = f"{self.base_path}/{name}"
        
        return self.client.put(path, json=data)
    
    def patch(
        self,
        name: str,
        data: Dict[str, Any],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Partially update an existing resource.
        
        Args:
            name: Resource name
            data: Partial resource data
            namespace: Optional namespace
        
        Returns:
            Updated resource object
        """
        if namespace:
            path = f"{self.base_path}/{namespace}/{name}"
        else:
            path = f"{self.base_path}/{name}"
        
        return self.client.patch(path, json=data)
    
    def delete(self, name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a resource.
        
        Args:
            name: Resource name
            namespace: Optional namespace
        
        Returns:
            Deletion response
        """
        if namespace:
            path = f"{self.base_path}/{namespace}/{name}"
        else:
            path = f"{self.base_path}/{name}"
        
        return self.client.delete(path)
