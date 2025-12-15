
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Settings resource manager
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Settings resource manager
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource


class Settings(BaseResource):
    """
    Manager for Harvester Settings.
    
    Provides methods to manage Harvester configuration settings.
    """
    
    def __init__(self, client):
        super().__init__(client)
        self.base_path = "/apis/harvesterhci.io/v1beta1/settings"
    
    def list(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all Harvester settings.
        
        Args:
            params: Additional query parameters
        
        Returns:
            List of setting objects
        """
        response = self.client.get(self.base_path, params=params)
        
        if isinstance(response, dict) and 'items' in response:
            return response['items']
        return response
    
    def get(self, name: str) -> Dict[str, Any]:
        """
        Get a specific setting.
        
        Args:
            name: Setting name
        
        Returns:
            Setting object
        """
        path = f"{self.base_path}/{name}"
        return self.client.get(path)
    
    def update(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a setting.
        
        Args:
            name: Setting name
            data: Updated setting data
        
        Returns:
            Updated setting object
        """
        path = f"{self.base_path}/{name}"
        return self.client.put(path, json=data)
    
    def patch(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Partially update a setting.
        
        Args:
            name: Setting name
            data: Partial setting data
        
        Returns:
            Updated setting object
        """
        path = f"{self.base_path}/{name}"
        return self.client.patch(path, json=data)
