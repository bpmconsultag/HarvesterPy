
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# HarvesterPy - A Python library to interface with SUSE Harvester HCI
#
# This library provides a Python interface to the SUSE Harvester HCI API.
# For more information about the Harvester API, see:
# https://docs.harvesterhci.io/v1.6/api/
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
HarvesterPy - A Python library to interface with SUSE Harvester HCI

This library provides a Python interface to the SUSE Harvester HCI API.
For more information about the Harvester API, see:
https://docs.harvesterhci.io/v1.6/api/
"""

from .client import HarvesterClient
from .exceptions import (
    HarvesterException,
    HarvesterAPIError,
    HarvesterAuthenticationError,
    HarvesterConnectionError,
    HarvesterNotFoundError,
)

__version__ = "0.1.0"
__all__ = [
    "HarvesterClient",
    "HarvesterException",
    "HarvesterAPIError",
    "HarvesterAuthenticationError",
    "HarvesterConnectionError",
    "HarvesterNotFoundError",
]
