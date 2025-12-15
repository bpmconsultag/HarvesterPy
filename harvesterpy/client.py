
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Main client for interacting with the Harvester HCI API
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Main client for interacting with the Harvester HCI API
"""

import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from .exceptions import (
    HarvesterAPIError,
    HarvesterAuthenticationError,
    HarvesterConnectionError,
    HarvesterNotFoundError,
)
from .resources.virtual_machines import VirtualMachines
from .resources.images import Images
from .resources.volumes import Volumes
from .resources.networks import Networks
from .resources.nodes import Nodes
from .resources.settings import Settings


class HarvesterClient:
    """
    Main client for interacting with the Harvester HCI API.
    
    Args:
        host: The Harvester host URL (e.g., 'https://harvester.example.com')
        token: API token for authentication
        username: Username for basic authentication (alternative to token)
        password: Password for basic authentication (alternative to token)
        verify_ssl: Whether to verify SSL certificates (default: True)
        timeout: Request timeout in seconds (default: 30)
    
    Example:
        >>> client = HarvesterClient(
        ...     host='https://harvester.example.com',
        ...     token='your-api-token'
        ... )
        >>> vms = client.virtual_machines.list()
    """
    
    def __init__(
        self,
        host: str,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: int = 30,
    ):
        self.host = host.rstrip('/')
        self.token = token
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        
        # Initialize session
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        # Set authentication
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}',
            })
        elif username and password:
            self.session.auth = (username, password)
        else:
            raise HarvesterAuthenticationError(
                "Either token or username/password must be provided"
            )
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        # Initialize resource managers
        self.virtual_machines = VirtualMachines(self)
        self.images = Images(self)
        self.volumes = Volumes(self)
        self.networks = Networks(self)
        self.nodes = Nodes(self)
        self.settings = Settings(self)
    
    def _build_url(self, path: str) -> str:
        """Build full URL from path"""
        if not path.startswith('/'):
            path = '/' + path
        return urljoin(self.host, path)
    
    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate exceptions"""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise HarvesterAuthenticationError(
                    "Authentication failed. Check your credentials."
                )
            elif response.status_code == 404:
                raise HarvesterNotFoundError(
                    "Resource not found",
                    status_code=404,
                    response=response
                )
            else:
                try:
                    error_data = response.json()
                    message = error_data.get('message', str(e))
                except Exception:
                    message = str(e)
                raise HarvesterAPIError(
                    message,
                    status_code=response.status_code,
                    response=response
                )
        
        # Return JSON if present, otherwise return response
        if response.content:
            try:
                return response.json()
            except (ValueError, requests.exceptions.JSONDecodeError):
                return response.text
        return None
    
    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Make an HTTP request to the Harvester API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path
            params: URL query parameters
            data: Form data to send
            json: JSON data to send
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            Response data (usually JSON)
        
        Raises:
            HarvesterConnectionError: If connection fails
            HarvesterAPIError: If API returns an error
        """
        url = self._build_url(path)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                timeout=self.timeout,
                **kwargs
            )
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            raise HarvesterConnectionError(f"Failed to connect to {url}: {e}")
        except requests.exceptions.Timeout as e:
            raise HarvesterConnectionError(f"Request timed out: {e}")
        except (HarvesterAuthenticationError, HarvesterAPIError, HarvesterNotFoundError):
            raise
        except Exception as e:
            raise HarvesterAPIError(f"Request failed: {e}")
    
    def get(self, path: str, **kwargs) -> Any:
        """Make a GET request"""
        return self.request('GET', path, **kwargs)
    
    def post(self, path: str, **kwargs) -> Any:
        """Make a POST request"""
        return self.request('POST', path, **kwargs)
    
    def put(self, path: str, **kwargs) -> Any:
        """Make a PUT request"""
        return self.request('PUT', path, **kwargs)
    
    def patch(self, path: str, **kwargs) -> Any:
        """Make a PATCH request"""
        return self.request('PATCH', path, **kwargs)
    
    def delete(self, path: str, **kwargs) -> Any:
        """Make a DELETE request"""
        return self.request('DELETE', path, **kwargs)
