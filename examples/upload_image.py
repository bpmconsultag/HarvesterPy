
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example: Import a disk image to Harvester from an URL
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

"""
Example: Import a disk image to Harvester from an URL
"""

#NOTE: For some reason, all s3 pulls fail with a 405
from harvesterpy import HarvesterClient
from datetime import datetime

# S3 pre-signed URL for your image
IMAGE_URL = "https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img"  # Replace with your pre-signed URL
IMAGE_NAME = "my-uploaded-image" + datetime.now().strftime("%Y%m%d%H%M%S")

# Connect to Harvester
client = HarvesterClient(
    host='https://your-harvester-host/',
    token='replaceme-with-your-token',
)


# Create the image resource in Harvester using the S3 URL (full resource object will be sent)
response = client.images.upload(
    name=IMAGE_NAME,
    file_path=None,  # Not needed for URL-based upload
    display_name="My Uploaded Image" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    description="Uploaded from URL",
    source_type="download",
    url=IMAGE_URL
)
print("Upload response:", response)

# Optionally, check image status
image = client.images.get(IMAGE_NAME)
print("Image status:", image.get("status", {}))
