##################################################################################
# VARIABLES
##################################################################################

# Credentials

variable "vsphere_server" {
  type = string
}

variable "vsphere_username" {
  type = string
  sensitive = true
}

variable "vsphere_password" {
  type = string
  sensitive = true
}

variable "vsphere_insecure" {
  type    = bool
  default = false
}

variable "vault_app_name" {
  type = string
  sensitive = true
}

# vSphere Settings

variable "vsphere_datacenter" {
  type = string
}

variable "vsphere_cluster" {
  type = string
}

variable "vsphere_datastore" {
  type = string
}

variable "vsphere_folder" {
  type = string
}

variable "vsphere_network" {
  type = string
}

variable "vsphere_content_library" {
  type = string
}

variable "vsphere_content_library_ovf" {
  type = string
}

variable "vsphere_host" {
  type = string
}

# Virtual Machine Settings

variable "vm_name" {
  type = string
}

variable "vm_cpus" {
  type = number
}

variable "vm_memory" {
  type = number
}

variable "vm_disk_size" {
  type = number
}

variable "vm_firmware" {
  type = string
}

variable "vm_efi_secure_boot_enabled" {
  type = bool
}

variable "vm_hostname" {
  type = string
}

variable "vm_domain" {
  type = string
}

variable "wait_for_guest_net_timeout" {
  type = number
  default = 5
}

variable "wait_for_guest_net_routable" {
  type = bool
  default = true
}
#variable "vm_ipv4_address" {
#  type = string
#}

#variable "vm_ipv4_netmask" {
#  type = string
#}

#variable "vm_ipv4_gateway" {
#  type = string
#}

#variable "vm_dns_suffix_list" {
#  type = list(string)
#}

#variable "vm_dns_server_list" {
#  type = list(string)
#}

#variable "domain" {
#  type = string
#}

#variable "domain_admin_username" {
#  type = string
#}

#variable "domain_admin_password" {
#  type = string
#}

variable "vm_admin_username" {
  type = string
  sensitive = true
}

variable "vm_admin_password" {
  type = string
}

# Port Group Settings

variable "pg_name" {
  type = string
  description = "name of port group"  
}

variable "pg_vlan_id" {
  type = number
  default = 4095
  description = "value of 0 means no vlan, 4095 means vm's can use any vlan, 1-4094 means use that vlan"
}

variable "pg_allow_promiscuous" {
  type = bool
  default = false
  description = "allow promiscuous mode on port group"
}



variable "HCP_CLIENT_ID" {
  type = string
}

variable "HCP_CLIENT_SECRET" {
  type = string
}