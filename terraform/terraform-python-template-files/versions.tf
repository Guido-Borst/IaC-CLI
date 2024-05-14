##################################################################################
# VERSIONS
##################################################################################

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
  }

  required_version = ">= 1.3.7"
}
