terraform {
  required_providers {
    vsphere = {
      source  = "hashicorp/vsphere"
      version = ">= 2.2.0"
    }
    ansible = {
      source  = "ansible/ansible"
      version = "~> 1.1.0"
    }
    hcp = {
      source = "hashicorp/hcp"
      version = "0.63.0"
    }
  }
}
provider "ansible" {
  # Configuration options
}

provider "hcp" {
  # Configuration options
  client_id     = var.HCP_CLIENT_ID
  client_secret = var.HCP_CLIENT_SECRET
}

data "hcp_vault_secrets_app" "WebApplication" {
  app_name = var.vault_app_name
}

provider "vsphere" {
  # vsphere_server       = var.vsphere_server
  vsphere_server       = data.hcp_vault_secrets_app.WebApplication.secrets.vsphere_server
  user                 = data.hcp_vault_secrets_app.WebApplication.secrets.vsphere_username
  password             = data.hcp_vault_secrets_app.WebApplication.secrets.vsphere_password
  allow_unverified_ssl = var.vsphere_insecure
}

data "vsphere_datacenter" "datacenter" {
  name = data.hcp_vault_secrets_app.WebApplication.secrets.vsphere_datacenter
}

data "vsphere_network" "network" {
  name          = var.vsphere_network
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_compute_cluster" "cluster" {
  name          = data.hcp_vault_secrets_app.WebApplication.secrets.vsphere_cluster
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_resource_pool" "pool" {
  name          = format("%s%s", data.vsphere_compute_cluster.cluster.name, "/Resources")
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_datastore" "datastore" {
  name          = data.hcp_vault_secrets_app.WebApplication.secrets.vsphere_datastore
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_content_library" "content_library" {
  name = data.hcp_vault_secrets_app.WebApplication.secrets.vsphere_content_library
}

data "vsphere_content_library_item" "content_library_item" {
  name       = var.vsphere_content_library_ovf
  type       = "ovf"
  library_id = data.vsphere_content_library.content_library.id
}

resource "vsphere_virtual_machine" "vm" {
  name                        = var.vm_name
  folder                      = data.hcp_vault_secrets_app.WebApplication.secrets.vsphere_folder
  num_cpus                    = var.vm_cpus
  memory                      = var.vm_memory
  firmware                    = var.vm_firmware
  efi_secure_boot_enabled     = var.vm_efi_secure_boot_enabled
  datastore_id                = data.vsphere_datastore.datastore.id
  resource_pool_id            = data.vsphere_resource_pool.pool.id
  wait_for_guest_net_timeout  = var.wait_for_guest_net_timeout
  wait_for_guest_net_routable = var.wait_for_guest_net_routable
  # guest_id                = data.vsphere_virtual_machine.template.guest_id
  network_interface {
    network_id = data.vsphere_network.network.id
  }
  disk {
    label            = "disk0"
    size             = var.vm_disk_size
    thin_provisioned = true
  }
  clone {
    template_uuid = data.vsphere_content_library_item.content_library_item.id
    customize {
      windows_options {
        computer_name         = var.vm_name
#        join_domain           = var.domain
#        domain_admin_user     = var.domain_admin_username
#        domain_admin_password = var.domain_admin_password
        admin_password        = data.hcp_vault_secrets_app.WebApplication.secrets.vm_admin_password
      }
      # linux_options {
      #   host_name = var.vm_hostname
      #   domain    = var.vm_domain
      # }
      network_interface {
#        ipv4_address = var.vm_ipv4_address
#        ipv4_netmask = var.vm_ipv4_netmask
      }

#      ipv4_gateway    = var.vm_ipv4_gateway
#      dns_suffix_list = var.vm_dns_suffix_list
#      dns_server_list = var.vm_dns_server_list
    }
  }

  lifecycle {
    ignore_changes = [
      clone[0].template_uuid,
    ]
  }
}

resource "ansible_host" "single_host" {          #### ansible host details
  name   = vsphere_virtual_machine.vm.guest_ip_addresses[0]
  groups = []
  variables = {
    ansible_user                 = data.hcp_vault_secrets_app.WebApplication.secrets.vm_admin_username,
    ansible_ssh_public_key_file  = "./id_ansible.pub",
    ansible_ssh_private_key_file = "./id_ansible",
    ansible_ssh_password         = data.hcp_vault_secrets_app.WebApplication.secrets.vm_admin_password,
    ansible_python_interpreter   = "/usr/bin/python3"

  }
}