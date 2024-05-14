Copyright 2024 Guido Borst. All Rights Reserved.

# Setup
This project is built with Python 3.10.12, but should be usable with most Python 3 versions. 
If you want to use a virtual environment, first run `python -m venv venv` to create a virtual environment, and then run `source venv/bin/activate` to activate the virtual environment. Then install the required Python packages by running `pip install -r requirements.txt` in the root of the project. 

To run the deploy-vms.py script, make sure you have Terraform and Ansible installed locally (see https://www.terraform.io/ and https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html). Also make sure to execute `ansible-galaxy collection install cloud.terraform` to install the ansible-terraform plugin. 

Since this project uses Hashicorp Vault for the secure usage of sensitive configuration parameters, create a new (free) Hashicorp Vault Secrets app (https://portal.cloud.hashicorp.com/services/secrets). 
Copy the name of the app, for example 'purple-lab-python-script', to the `terraform/terraform-python-template-files/terraform.tfvars` file under `vault_app_name`.

Then, create the following secrets in the Hashicorp Vault Secrets app: 
- vm_admin_username       (The username for the local administrator account on the VMs, also used as build_username in Packer phase)
- vm_admin_password        (The password for the local administrator account on the VMs, also used as build_password in Packer phase)
- vsphere_server         (The name/IP of the vSphere server)
- vsphere_username      (The username for the vSphere user to deploy the VMs with)
- vsphere_password         (The password for the vSphere user to deploy the VMs with)
- vsphere_datacenter      (The name of the vSphere datacenter to deploy the VMs to)
- vsphere_cluster          (The name of the vSphere cluster to deploy the VMs to)
- vsphere_datastore       (The name of the vSphere datastore to deploy the VMs to)
- vsphere_content_library   (The name of the vSphere content library to deploy the VMs from)
- vsphere_folder           (The path to the virtual machine folder in which to place the virtual machine, relative to the datacenter path) 
- vsphere_host            (The name/IP of the vSphere host to deploy the VMs to)

In Hashicorp Vault Secrets, create a new service principal (https://portal.cloud.hashicorp.com/access/service-principals) and copy the client id and client secret to the `terraform/terraform-python-template-files/terraform.tfvars` file under `HCP_CLIENT_ID` and `HCP_CLIENT_SECRET` respectively.

Additionally, replace the vm_domain variable in the `terraform/terraform-python-template-files/terraform.tfvars` file with the domain name of your VMs. 

Finally, in HashiCorp Vault Secrets, click on 'How to use your secrets' button, go to the API tab, and in the third step called 'Read your secrets', copy the 'location' parameter of the curl command to the `organization_url` parameter in the `load_library_items` function in the `deploy-vms.py` script.



# Features
- User friendly way to deploy VMs from a vSphere content library using Terraform
- Per-VM configuration using Ansible playbooks
- Create new vSphere port-groups for the VMs, and optionally setup a DHCP-server on the new port-groups
- Use Hashicorp Vault for the secure usage of sensitive configuration parameters



# Usage
After having created vSphere content library items for the VMs you want to deploy, for example by running the `build.sh` script, run the `deploy-vms.py` script and follow the instructions. 



# Improvements
There are still some improvements that can be made to this project:
- Use multithreading to speed up the deployment of the VMs
- Add support for using vTPM cards, so we don't have to bypass the TPM check in Windows 11
- Use a ssh key to connect to the VMs instead of a password. This would require uploading an ssh key in the Packer-phase, when creating the VM images.


