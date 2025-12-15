# Ansible Role: harvesterpy

An Ansible role for managing SUSE Harvester HCI resources using the harvesterpy Python library.

## Description

This role provides Ansible modules to manage virtual machines, images, volumes, and networks in SUSE Harvester HCI. It wraps the harvesterpy Python library to offer idempotent, declarative infrastructure management through Ansible playbooks.

## Requirements

- Ansible 2.10 or higher
- Python 3.8 or higher
- harvesterpy Python library (see below for local development)
- Access to a SUSE Harvester HCI cluster

## Installation

### From Ansible Galaxy (when published)


```bash
ansible-galaxy install bpmconsultag.harvesterpy
```

### From Source



```bash
git clone https://github.com/bpmconsultag/harvesterpy.git
cd harvesterpy/ansible/roles
ansible-galaxy install -r harvesterpy/requirements.yml
```

Or reference the role directly in your playbook from the repository.

## Using the Local harvesterpy Library for Development

If you are developing or testing with the local harvesterpy source (not the PyPI package), you must install it into your Python environment:

From the root of the repository:

```bash
cd /path/to/harvesterpy  # project root containing setup.py or pyproject.toml
pip install -e .
```

Alternatively, you can set the `PYTHONPATH` environment variable before running Ansible:

```bash
export PYTHONPATH=$PWD:$PYTHONPATH
```
This should be run from the project root.

If you see errors about the harvesterpy library not being found, ensure you have performed one of the above steps in the same environment where Ansible runs.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Harvester API connection settings
harvester_host: ""                    # Harvester host URL (required)
harvester_token: ""                   # API token for authentication
harvester_verify_ssl: true            # Verify SSL certificates
harvester_timeout: 30                 # Request timeout in seconds

# Default namespace for resources
harvester_namespace: "default"

# VM defaults
harvester_vm_state: "present"         # State: present, absent, started, stopped, restarted
harvester_vm_running: true            # Whether VM should be running
harvester_vm_cpu_cores: 2             # Default CPU cores
harvester_vm_memory: "4Gi"            # Default memory allocation

# Image defaults
harvester_image_state: "present"      # State: present, absent

# Volume defaults
harvester_volume_state: "present"     # State: present, absent
harvester_volume_access_modes:        # Default access modes
  - ReadWriteOnce
harvester_volume_storage: "10Gi"      # Default storage size

# Network defaults
harvester_network_state: "present"    # State: present, absent
```

## Modules

The role includes the following custom Ansible modules:

### harvester_vm

Manage virtual machines in Harvester.

**Parameters:**
- `host`: Harvester host URL (required)
- `token` or `username`/`password`: Authentication credentials (required)
- `name`: VM name (required)
- `namespace`: Namespace (default: "default")
- `state`: Desired state (present, absent, started, stopped, restarted)
- `cpu_cores`: Number of CPU cores
- `memory`: Memory allocation
- `disks`: List of disk configurations
- `networks`: List of network configurations
- `labels`: Labels to apply to the VM
- `spec`: Complete VM specification (advanced)

### harvester_image

Manage VM images in Harvester.

**Parameters:**
- `host`: Harvester host URL (required)
- `token` or `username`/`password`: Authentication credentials (required)
- `name`: Image name (required)
- `namespace`: Namespace (default: "default")
- `state`: Desired state (present, absent)
- `url`: URL to download the image from
- `display_name`: Display name for the image
- `description`: Description of the image
- `source_type`: Source type (download, upload)
- `storage_class`: Storage class for the image
- `labels`: Labels to apply to the image

### harvester_volume

Manage persistent volumes in Harvester.

**Parameters:**
- `host`: Harvester host URL (required)
- `token` or `username`/`password`: Authentication credentials (required)
- `name`: Volume name (required)
- `namespace`: Namespace (default: "default")
- `state`: Desired state (present, absent)
- `storage`: Storage size (e.g., "10Gi")
- `access_modes`: Access modes (default: ["ReadWriteOnce"])
- `storage_class`: Storage class for the volume
- `volume_mode`: Volume mode (Filesystem, Block)
- `labels`: Labels to apply to the volume

### harvester_network

Manage network attachment definitions in Harvester.

**Parameters:**
- `host`: Harvester host URL (required)
- `token` or `username`/`password`: Authentication credentials (required)
- `name`: Network name (required)
- `namespace`: Namespace (default: "default")
- `state`: Desired state (present, absent)
- `config`: Network configuration (JSON string or dict)
- `labels`: Labels to apply to the network

## Dependencies

This role has no dependencies on other Ansible roles. It will automatically install the `harvesterpy` Python library when tasks are executed.

## Example Playbooks

### Basic VM Creation

```yaml
---
- name: Create a VM in Harvester
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Create virtual machine
      harvester_vm:
        host: "https://harvester.example.com"
        token: "your-api-token"
        name: "my-vm"
        namespace: "default"
        state: present
        cpu_cores: 2
        memory: "4Gi"
```

### Complete VM Deployment with Image and Volume

```yaml
---
- name: Deploy complete VM with dependencies
  hosts: localhost
  gather_facts: false
  vars:
    harvester_host: "https://harvester.example.com"
    harvester_token: "your-api-token"
  
  tasks:
    - name: Create VM image
      harvester_image:
        host: "{{ harvester_host }}"
        token: "{{ harvester_token }}"
        name: "ubuntu-20.04"
        state: present
        url: "https://cloud-images.ubuntu.com/releases/focal/release/ubuntu-20.04-server-cloudimg-amd64.img"
        display_name: "Ubuntu 20.04 LTS"

    - name: Create VM volume
      harvester_volume:
        host: "{{ harvester_host }}"
        token: "{{ harvester_token }}"
        name: "my-vm-disk"
        state: present
        storage: "20Gi"

    - name: Create virtual machine
      harvester_vm:
        host: "{{ harvester_host }}"
        token: "{{ harvester_token }}"
        name: "my-ubuntu-vm"
        state: present
        cpu_cores: 4
        memory: "8Gi"
        disks:
          - name: disk0
            volume_name: "my-vm-disk"
            bus: virtio
        labels:
          environment: production
```

### VM Lifecycle Management

```yaml
---
- name: Manage VM lifecycle
  hosts: localhost
  gather_facts: false
  vars:
    harvester_host: "https://harvester.example.com"
    harvester_token: "your-api-token"
    vm_name: "my-vm"
  
  tasks:
    - name: Stop VM
      harvester_vm:
        host: "{{ harvester_host }}"
        token: "{{ harvester_token }}"
        name: "{{ vm_name }}"
        state: stopped

    - name: Start VM
      harvester_vm:
        host: "{{ harvester_host }}"
        token: "{{ harvester_token }}"
        name: "{{ vm_name }}"
        state: started

    - name: Restart VM
      harvester_vm:
        host: "{{ harvester_host }}"
        token: "{{ harvester_token }}"
        name: "{{ vm_name }}"
        state: restarted
```

### Using with Role

```yaml
---
- name: Use harvesterpy role
  hosts: localhost
  roles:
    - role: bpmconsultag.harvesterpy
      vars:
        harvester_host: "https://harvester.example.com"
        harvester_token: "your-api-token"
  
  tasks:
    - name: Create VM using role defaults
      harvester_vm:
        host: "{{ harvester_host }}"
        token: "{{ harvester_token }}"
        name: "test-vm"
        state: present
```

## Example Playbooks in Repository


## Running Example Playbooks


When running the example playbooks, you must specify the custom module path so Ansible can find the harvester modules:

```sh
# If you are in the ansible/roles/harvesterpy directory:
ansible-playbook -i examples/inventory.ini examples/create_vm.yml --module-path=library -e "harvester_verify_ssl=false"

# Or from the project root:
ansible-playbook -i ansible/roles/harvesterpy/examples/inventory.ini ansible/roles/harvesterpy/examples/create_vm.yml --module-path=ansible/roles/harvesterpy/library -e "harvester_verify_ssl=false"
```

This ensures Ansible loads the modules from the `library/` directory in this role. If you see errors like `couldn't resolve module/action 'harvester_image'`, make sure to use the `--module-path` option as shown above.

The role includes several example playbooks in the `examples/` directory:

- `create_vm.yml`: Complete VM creation with image and volume
- `manage_vm_lifecycle.yml`: Start, stop, and restart operations
- `cleanup.yml`: Remove all created resources
- `inventory.ini`: Example inventory file

## Best Practices

1. **Use Ansible Vault for Credentials**: Store sensitive information like tokens and passwords in Ansible Vault:
   ```bash
   ansible-vault create group_vars/all/vault.yml
   ```

2. **Idempotency**: All modules are idempotent. Running the same playbook multiple times will not create duplicate resources.

3. **Check Mode**: All modules support Ansible's check mode (`--check`) for dry runs.

4. **Tags**: Use tags to organize your playbooks:
   ```yaml
   - name: Create VM
     harvester_vm:
       # ...
     tags: [harvester, vm, create]
   ```

5. **Error Handling**: Use `ignore_errors` and `failed_when` for better error handling:
   ```yaml
   - name: Delete VM (may not exist)
     harvester_vm:
       name: "my-vm"
       state: absent
     ignore_errors: true
   ```

## Troubleshooting

### Module not found

If Ansible cannot find the modules, ensure the role is properly installed and the library path is correct:

```bash
export ANSIBLE_LIBRARY=/path/to/harvesterpy/ansible/roles/harvesterpy/library:$ANSIBLE_LIBRARY
```

### harvesterpy not installed


If you encounter issues with the harvesterpy library not being found, ensure you have installed it as described above. For production or non-development use, you can install from PyPI:

```bash
pip install harvesterpy
```

### SSL Certificate Verification

If you're using self-signed certificates, you can disable SSL verification (not recommended for production):

```yaml
harvester_verify_ssl: false
```

## Testing

To test the role locally:

1. Set up your Harvester connection details in a vars file
2. Run the example playbooks:
   ```bash
   ansible-playbook -i examples/inventory.ini examples/create_vm.yml
   ```

## Contributing

Contributions are welcome! Please submit pull requests or issues to the [GitHub repository](https://github.com/bpmconsultag/harvesterpy).

## License

MIT

## Author Information

This role was created by bpmconsultag as part of the harvesterpy project.

## Links

- [HarvesterPy GitHub Repository](https://github.com/bpmconsultag/harvesterpy)
- [SUSE Harvester Documentation](https://docs.harvesterhci.io/)
- [Harvester API Documentation](https://docs.harvesterhci.io/v1.6/api/)
