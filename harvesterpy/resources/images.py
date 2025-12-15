
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Image resource manager
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Image resource manager
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource


class Images(BaseResource):
    """
    Manager for VM Image resources in Harvester.
    
    Provides methods to manage VM images including uploading,
    listing, and deletion.
    """
    
    def __init__(self, client):
        super().__init__(client)
        self.base_path = "/apis/harvesterhci.io/v1beta1/namespaces"
    
    def upload(
        self,
        name: str,
        file_path: str = None,
        namespace: str = "default",
        display_name: str = None,
        description: str = None,
        storage_class: str = None,
        source_type: str = "download",
        url: str = None,
    ) -> dict:
        """
        Upload a disk image file to Harvester.
        Args:
            name: Name for the image resource
            file_path: Path to the local image file
            namespace: Namespace to upload to (default: "default")
            display_name: Optional display name
            description: Optional description
            storage_class: Optional storage class
            source_type: Source type (default: "download")
        Returns:
            Created image object
        """
        path = f"{self.base_path}/{namespace}/virtualmachineimages"
        if url and not file_path:
            # Build full VirtualMachineImage resource object for URL-based import
            resource = {
                "apiVersion": "harvesterhci.io/v1beta1",
                "kind": "VirtualMachineImage",
                "metadata": {
                    "name": name,
                    "namespace": namespace
                },
                "spec": {
                    "displayName": display_name or name,
                    "description": description or "",
                    "storageClassName": storage_class or "",
                    "sourceType": source_type,
                    "url": url
                }
            }
            # Remove empty fields in spec
            resource["spec"] = {k: v for k, v in resource["spec"].items() if v}
            return self.client.post(path, json=resource)
        else:
            data = {
                "name": name,
                "displayName": display_name or name,
                "description": description or "",
                "storageClassName": storage_class or "",
                "sourceType": source_type,
            }
            # Remove empty fields
            data = {k: v for k, v in data.items() if v}
            if file_path:
                with open(file_path, "rb") as f:
                    files = {
                        "file": (name, f, "application/octet-stream"),
                    }
                    return self.client.post(path, files=files, data=data)
            else:
                return self.client.post(path, json=data)

    def list(
        self,
        namespace: str = "default",
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all VM images in a namespace.
        
        Args:
            namespace: Namespace to list images from (default: "default")
            params: Additional query parameters
        
        Returns:
            List of image objects
        """
        path = f"{self.base_path}/{namespace}/virtualmachineimages"
        response = self.client.get(path, params=params)
        
        if isinstance(response, dict) and 'items' in response:
            return response['items']
        return response
    
    def get(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get a specific VM image.
        
        Args:
            name: Image name
            namespace: Namespace (default: "default")
        
        Returns:
            Image object
        """
        path = f"{self.base_path}/{namespace}/virtualmachineimages/{name}"
        return self.client.get(path)
    
    def create(
        self,
        data: Dict[str, Any],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a new VM image.
        
        Args:
            data: Image specification data
            namespace: Namespace (default: "default")
        
        Returns:
            Created image object
        """
        path = f"{self.base_path}/{namespace}/virtualmachineimages"
        return self.client.post(path, json=data)
    
    def update(
        self,
        name: str,
        data: Dict[str, Any],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Update a VM image.
        
        Args:
            name: Image name
            data: Updated image specification
            namespace: Namespace (default: "default")
        
        Returns:
            Updated image object
        """
        path = f"{self.base_path}/{namespace}/virtualmachineimages/{name}"
        return self.client.put(path, json=data)
    
    def delete(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a VM image.
        
        Args:
            name: Image name
            namespace: Namespace (default: "default")
        
        Returns:
            Deletion response
        """
        path = f"{self.base_path}/{namespace}/virtualmachineimages/{name}"
        return self.client.delete(path)
