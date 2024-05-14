# Copyright 2024 Guido Borst. All Rights Reserved.

import datetime
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient

from selectionmenu import *


import shutil
import tempfile
import os
import subprocess
import hcl2
import json
import signal 
# import time
import requests

class ListLibraryItems(SampleBase):
    """
    Demonstrates the basic operations of a content library. The sample also
    demonstrates the interoperability of the VIM and vAPI.

    Note: the workflow needs an existing VC DS with available storage.

    """

    def __init__(self, server=None, username=None, password=None, datastorename=None, print=False):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.datastore_name = None
        self.lib_name = "demo-local-lib"
        self.local_library = None
        if server is not None:
            self.server = server
            self.username = username
            self.password = password
            self.datastore_name = datastorename
            self.skip_verification = True
        self.library_items_list = []
        self.print = print

    def _options(self):
        self.argparser.add_argument('-datastorename',
                                    '--datastorename',
                                    help='The name of the datastore.')

    def _setup(self):
        if not self.datastore_name:
            self.datastore_name = self.args.datastorename
        assert self.datastore_name is not None

        if not self.servicemanager:
            self.servicemanager = self.get_service_manager()

        self.client = ClsApiClient(self.servicemanager)

    def list_library_items(self):
        # List of visible content libraries
        visible_cls = self.client.local_library_service.list()
        if len(visible_cls) > 0:
            for visible_cl in visible_cls:
                get_visible_cl = self.client.local_library_service.get(visible_cl)
                if self.print:
                    print('Visible content library: {0} with id: {1}'.format(get_visible_cl.name, visible_cl))
                for libraryitem in self.client.library_item_service.list(visible_cl):
                    # print('Visible Item: {0} with id: {1}'.format(libraryitem.name, libraryitem))
                    libitem = self.client.library_item_service.get(libraryitem)
                    if self.print:
                        print('Visible Item: {0} with id: {1}'.format(libitem.name, libitem.id))
                    self.library_items_list.append(libitem)
        return self.library_items_list

    def _execute(self):
        return self.list_library_items()

    def _cleanup(self):
        if self.local_library:
            # self.client.local_library_service.delete(library_id=self.local_library.id)
            print('NOT Deleted Library Id: {0}'.format(self.local_library.id))


# Load the library items from the vSphere Content Library
def load_library_items(tvars_file, print_items=False):
    # Define the URL to access the HashiCorp Vault Secrets (see https://portal.cloud.hashicorp.com/services/secrets/apps/<app-name>/secrets/ and scroll down to API)
    organization_url = 'https://api.cloud.hashicorp.com/secrets/<REPLACE_THIS_PART>'

    # Read the terraform.tfvars file to access Vault variables
    with open(tvars_file) as f:
        data = hcl2.load(f)

    # Get short-lived API token to access HaschiCorp Vault Secrets using client id and secret
    headers = {'content-type': 'application/json'}
    payload = {
        "audience": "https://api.hashicorp.cloud",
        "grant_type": "client_credentials",
        "client_id": data['HCP_CLIENT_ID'],
        "client_secret": data['HCP_CLIENT_SECRET']
    }
    response = requests.post('https://auth.hashicorp.com/oauth/token', headers=headers, data=json.dumps(payload))
    HCP_API_TOKEN = response.json()['access_token']

    # Read the secrets from HashiCorp Vault Secrets
    headers = {'Authorization': f'Bearer {HCP_API_TOKEN}'}
    response = requests.get(organization_url, headers=headers)
    secrets = response.json()

    # Parse the secrets into a dictionary
    secret_names = ['vsphere_server', 'vsphere_username', 'vsphere_password', 'vsphere_datacenter', 'vsphere_datastore']
    secrets_dict = {name: None for name in secret_names}
    for secret in secrets['secrets']:
        if secret['name'] in secrets_dict:
            secrets_dict[secret['name']] = secret['version']['value']        

    # Load the library items from the vSphere Content Library
    libraryclass = ListLibraryItems(server=secrets_dict['vsphere_server'], username=secrets_dict['vsphere_username'] , password=secrets_dict['vsphere_password'], datastorename=secrets_dict['vsphere_datastore'])
    libraryclass._setup()
    library_list = libraryclass.list_library_items()
    library_list_name = []
    max_name_length = max(len(item.name) for item in library_list)
    for item in library_list:
        library_list_name.append(item.name)
        name = item.name.ljust(max_name_length)
        if print_items:
            print(name, " with id: ", item.id)
    return library_list, library_list_name


# Write a dictionary to a HCL file
def write_dict_to_file(dict_obj, filename):
    with open(filename, 'w') as f:
        for key, value in dict_obj.items():
            if isinstance(value, str):
                print(f'{key} = "{value}"', file=f)
            elif isinstance(value, bool):
                print(f'{key} = {str(value).lower()}', file=f)
            else:
                print(f'{key} = {value}', file=f)


# Run a list of shell-commands in a directory
def run_commands(commands, directory, print_output=True):
    global sub_process, received_sigint 
    received_sigint = False 
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal_handler)  # Register signal handler

    # Execute the command in the directory and wait for it to finish
    for command in commands:
        if received_sigint:
            break

        sub_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=directory)
        # Read the output line by line and print it to the console in real-time
        while True:
            output = sub_process.stdout.readline()
            if output == b'' and sub_process.poll() is not None:
                break
            if output and print_output:
                print(output.decode('utf-8').rstrip())

        # Print the error to the console
        error = sub_process.stderr.read()
        print(error.decode('utf-8'))

    signal.signal(signal.SIGINT, original_sigint_handler)  # Restore original signal handler
    return 



def signal_handler(sig, frame):
    print('Forwarding SIGINT to subprocess')
    global received_sigint
    received_sigint = True
    if sub_process:
        sub_process.send_signal(signal.SIGINT)



def create_port_group(global_settings, pg_name, vlan_id, promiscuous=True, dhcp=False):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="terraform-python-tmp", dir=global_settings['temp-dir'])

    # Define the source files to copy
    source_files = ["./terraform/terraform-python-template-files/create-host-port-group.tf", 
                    "./terraform/terraform-python-template-files/terraform.tfvars", 
                    "./terraform/terraform-python-template-files/variables.tf"]

    # Copy each file to the temporary directory
    for source_file in source_files:
        shutil.copy(source_file, temp_dir)

    # Update the terraform.tvars file 
    with open(f"{temp_dir}/terraform.tfvars", "r") as f:
        data = hcl2.load(f)
        data['pg_name'] = pg_name
        data['pg_vlan_id'] = vlan_id
        data['pg_allow_promiscuous'] = True

    # Write the modiffied terraform.tfvars file
    write_dict_to_file(data, f"{temp_dir}/terraform.tfvars")

    # Print the path of the temporary directory
    print(f"Files have been copied to {temp_dir}")

    commands = ['#ls -lah', 'terraform init', '#ls -lah', '#terraform plan', 'terraform apply -auto-approve', 'sleep 5']
    run_commands(commands, temp_dir)

    deploy_linux_ovf('DHCP-server', {'port_group': pg_name, 'playbooks': []}, {'project_name': pg_name, 'temp-dir': global_settings['temp-dir']}, dhcp=True)

    # remove the temporary directory
    print(f"Done, Removing {temp_dir}")
    shutil.rmtree(temp_dir)


# Execute Ansible playbooks on a VM
def execute_playbooks(vm_setting, temp_dir):
    if len(vm_setting['playbooks']) > 0:
        # Copy ansible files to the temporary directory
        shutil.copytree(f"./ansible/inventory", f"{temp_dir}/inventory")
        shutil.copytree(f"./ansible/roles", f"{temp_dir}/roles")
        # shutil.copy(f"{temp_dir}/terraform.tfstate", f"{temp_dir}/inventory")
        for playbook in vm_setting['playbooks']:
            shutil.copy(f"./ansible/{playbook}", temp_dir)
        # Execute the ansible playbooks
        commands = [f'ansible-playbook -i {temp_dir}/inventory *.yml']
        run_commands(commands, temp_dir)


def deploy_linux_ovf(library_item_name, vm_setting, global_settings=None, dhcp=False):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="terraform-python-tmp", dir=global_settings['temp-dir'])

    # Define the source files to copy
    source_files = ["./terraform/terraform-python-template-files/deploy-ovf-linux.tf", 
                    "./terraform/terraform-python-template-files/terraform.tfvars", 
                    "./terraform/terraform-python-template-files/variables.tf"]

    # Copy each file to the temporary directory
    for source_file in source_files:
        shutil.copy(source_file, temp_dir)

    # Edit the terraform.tvars file (is a json file)
    with open(f"{temp_dir}/terraform.tfvars", "r") as f:
        data = hcl2.load(f)
        data['vsphere_network'] = vm_setting['port_group']
        data['vm_name'] = f'{global_settings["project_name"]}-{library_item_name}-{datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")}'
        data['pg_allow_promiscuous'] = True
        data['vsphere_content_library_ovf'] = library_item_name

        # Update the VM settings for a small DHCP-server
        if dhcp:
            data['vm_cpus'] = 1
            data['vm_memory'] = 1024
            data['vm_disk_size'] = 20
            data['vm_firmware'] = 'bios'
            data['vm_efi_secure_boot_enabled'] = False
            data['wait_for_guest_net_timeout'] = 0
            data['wait_for_guest_net_routable'] = False

    # Write the modiffied terraform.tfvars file
    write_dict_to_file(data, f"{temp_dir}/terraform.tfvars")

    # Print the path of the temporary directory
    print(f"Files have been copied to {temp_dir}")

    commands = ['terraform init', 'terraform apply -auto-approve']
    run_commands(commands, temp_dir)

    if not dhcp: # The DHCP-server doesn't need Ansible playbooks, as the image is already configured
        execute_playbooks(vm_setting, temp_dir)

    # remove the temporary directory
    print(f"Done, Removing {temp_dir}")
    shutil.rmtree(temp_dir)



def deploy_windows_ovf(library_item_name, vm_setting, global_settings=None, dhcp=False):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="terraform-python-tmp", dir=global_settings['temp-dir'])

    # Define the source files to copy
    source_files = ["./terraform/terraform-python-template-files/deploy-ovf-windows.tf", 
                    "./terraform/terraform-python-template-files/terraform.tfvars", 
                    "./terraform/terraform-python-template-files/variables.tf"]

    # Copy each file to the temporary directory
    for source_file in source_files:
        shutil.copy(source_file, temp_dir)

    # Edit the terraform.tvars file (is a json file)
    with open(f"{temp_dir}/terraform.tfvars", "r") as f:
        data = hcl2.load(f)
        data['vsphere_network'] = vm_setting['port_group']
        data['vm_name'] = f'{global_settings["project_name"]}-{library_item_name}-{datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")}'
        data['pg_allow_promiscuous'] = True
        data['vsphere_content_library_ovf'] = library_item_name

    # Write the modiffied terraform.tfvars file
    write_dict_to_file(data, f"{temp_dir}/terraform.tfvars")

    # Print the path of the temporary directory
    print(f"Files have been copied to {temp_dir}")

    commands = ['terraform init', 'terraform apply -auto-approve']
    run_commands(commands, temp_dir)

    execute_playbooks(vm_setting, temp_dir)

    # remove the temporary directory
    print(f"Done, Removing {temp_dir}")
    shutil.rmtree(temp_dir)


# Ask the user general questions about the project
def ask_project_questions():
    settings = {
        'port_groups': [],
        'project_name': None,
        'temp-dir': '/tmp/',
    }

    settings['project_name'] = input("What is the project name (used for naming VMs)? (default 'ProjectA'): ") or 'ProjectA'
    settings['temp_dir'] = input("What is the temporary directory to work from? If available, use a Ramdisk. (default '/tmp/'): ") or '/tmp/'
    
    while True:
        create_port_group = input("Do you want to create a new port-group? (y/N): ")
        if create_port_group.lower() == 'y':
            port_group_name = input("\nEnter the name of the port-group: ")
            vlan_id = input("\nEnter the VLAN ID (default 0): ") or '0'
            allow_promiscuous = input("\nAllow promiscuous mode? (Y/n): ") or 'y'
            allow_promiscuous = allow_promiscuous.lower() == 'y'
            settings['port_groups'].append({
                'name': port_group_name,
                'vlan_id': vlan_id,
                'allow_promiscuous': allow_promiscuous,
                'dhcp': False,
            })
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Settings for Port-group '{port_group_name}':\nVLAN ID: '{vlan_id}'\nPromiscuous mode: '{allow_promiscuous}'\n")            
            confirm = input("\nDo you want to confirm these settings? (Y/n): ") or 'y'
            if confirm.lower() != 'y':
                settings['port_groups'].pop()
            else:
                setup_dhcp = input("\nDo you want to setup a DHCP-server in this port group? (Y/n): ") or 'y'
                if setup_dhcp.lower() == 'y':
                    settings['port_groups'][-1]['dhcp'] = True
        else:
            break
        os.system('cls' if os.name == 'nt' else 'clear')

    return settings



def ask_vm_questions(selections, library_items_name, global_settings):
    # Initialize the dictionary to store the answers
    answers = {}

    # List all the Ansible playbooks in the ./ansible directory
    playbooks = [file for file in os.listdir('./ansible') if file.endswith('.yml')]
    # playbooks = [file for file in os.listdir('./ansible') if file.endswith('.yml') or file.endswith('.yaml')]

    # Ask the questions for each VM
    for item_name, count in zip(library_items_name, selections):
        answers[item_name] = []  # Initialize the list of answers for this library item
        for _ in range(count):
            # Ask the name of the port-group
            if len(global_settings['port_groups']) > 0:
                # If we have created a new port-group, use that one as default
                default = global_settings['port_groups'][0]['name']
                port_group = input(f"\nWhat is the name of the port-group for {item_name}? (default '{default}'): ") or f'{default}'
            else:
                port_group = input(f"\nWhat is the name of the port-group for {item_name}? (default 'VM Network'): ") or 'VM Network'

            # Ask which Ansible playbooks to execute
            print("\nWhich Ansible playbooks should be executed on this VM? (default none)")
            for i, playbook in enumerate(playbooks, start=1):
                print(f"{i}. {playbook}")
            playbook_indices = input("\nEnter the numbers of the playbooks (separated by spaces), or press Enter to select none: ")
            selected_playbooks = [playbooks[int(index) - 1] for index in playbook_indices.split()] if playbook_indices else []

            # Ask whether this is a Linux or Windows PC
            default_os = 'windows' if 'windows' in item_name.lower() else 'linux'
            os_type = input(f"\nIs this a Linux or Windows PC? (detected: {default_os}): ") or default_os

            # Store the answers in the dictionary
            answers[item_name].append({
                'port_group': port_group,
                'playbooks': selected_playbooks,
                'os_type': os_type,
            })

            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Settings for VM '{item_name}':\nPort-group: '{port_group}'\nPlaybooks: {selected_playbooks}\nOS type: '{os_type}'\n")
            confirm = input("\nDo you want to confirm these settings? (Y/n): ") or 'y'
            if confirm.lower() != 'y':
                answers[item_name].pop()

            os.system('cls' if os.name == 'nt' else 'clear')

    return answers



def main():
    global sub_process, received_sigint
    sub_process = None
    received_sigint = False
    global_settings = ask_project_questions()
    
    library_items, library_items_name = load_library_items('./terraform/terraform-python-template-files/terraform.tfvars', print_items=False)
    selections = make_menu_selection(options=library_items_name, menu_text="Select Library Item(s) to deploy using cursor keys", bool_input=False)
    vm_settings = ask_vm_questions(selections, library_items_name, global_settings)

    # Create the port-groups
    for pg in global_settings['port_groups']:
        create_port_group(global_settings, pg['name'], pg['vlan_id'], pg['allow_promiscuous'], pg['dhcp'])
    
    # Deploy the VMs
    for item_name, item_settings in vm_settings.items():
        for settings in item_settings:
            if settings['os_type'].lower() == 'linux':
                deploy_linux_ovf(item_name, settings, global_settings)
            elif settings['os_type'].lower() == 'windows':
                deploy_windows_ovf(item_name, settings, global_settings)
                # print("Windows not supported yet")



if __name__ == '__main__':
    main()
