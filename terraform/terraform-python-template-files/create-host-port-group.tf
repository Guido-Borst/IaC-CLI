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

data "vsphere_host" "host" {
  name          = data.hcp_vault_secrets_app.WebApplication.secrets.vsphere_host
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

# resource "vsphere_host_virtual_switch" "host_virtual_switch" {
#   name           = "switch-01"
#   host_system_id = data.vsphere_host.host.id

#   network_adapters = ["vmnic0", "vmnic1"]

#   active_nics  = ["vmnic0"]
#   standby_nics = ["vmnic1"]
# }

resource "vsphere_host_port_group" "pg" {
  name                = var.pg_name
  host_system_id      = data.vsphere_host.host.id
  virtual_switch_name = "vSwitch0"

  vlan_id = var.pg_vlan_id

  allow_promiscuous = var.pg_allow_promiscuous
}
