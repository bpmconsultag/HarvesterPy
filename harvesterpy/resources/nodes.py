
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Node resource manager
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Node resource manager
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource


class Nodes(BaseResource):
    """
    Manager for Node resources in Harvester.
    
    Provides methods to manage cluster nodes.
    """
    
    def __init__(self, client):
        super().__init__(client)
        self.base_path = "/api/v1/nodes"
    
    def list(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all nodes in the cluster.
        
        Args:
            params: Additional query parameters
        
        Returns:
            List of node objects
        """
        response = self.client.get(self.base_path, params=params)
        
        if isinstance(response, dict) and 'items' in response:
            return response['items']
        return response
    
    def get(self, name: str) -> Dict[str, Any]:
        """
        Get a specific node.
        
        Args:
            name: Node name
        
        Returns:
            Node object
        """
        path = f"{self.base_path}/{name}"
        return self.client.get(path)
    
    def update(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a node.
        
        Args:
            name: Node name
            data: Updated node specification
        
        Returns:
            Updated node object
        """
        path = f"{self.base_path}/{name}"
        return self.client.put(path, json=data)
    
    def patch(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Partially update a node.
        
        Args:
            name: Node name
            data: Partial node data
        
        Returns:
            Updated node object
        """
        path = f"{self.base_path}/{name}"
        return self.client.patch(path, json=data)
