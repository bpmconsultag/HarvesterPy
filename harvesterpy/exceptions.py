
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Exceptions for the HarvesterPy library
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Exceptions for the HarvesterPy library
"""


class HarvesterException(Exception):
    """Base exception for all Harvester-related errors"""
    pass


class HarvesterAPIError(HarvesterException):
    """Raised when the Harvester API returns an error response"""
    
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class HarvesterAuthenticationError(HarvesterException):
    """Raised when authentication with Harvester fails"""
    pass


class HarvesterConnectionError(HarvesterException):
    """Raised when connection to Harvester fails"""
    pass


class HarvesterNotFoundError(HarvesterAPIError):
    """Raised when a resource is not found (404)"""
    pass
