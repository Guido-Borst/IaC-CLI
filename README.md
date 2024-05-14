# Infrastructure as Code Command Line Interface
The Infrastructure as Code Command Line Interface (IaC CLI) is an infrastructure deployment orchestration for small lab environments. It is a modular and easily extendable way to securely deploy infrastructure, with very few user input required and no CI/CD dependency. The IaC CLI is built mainly to be used with vSphere, although modifying it to work with AWS should be easy to do. 

From a high-level overview the project has three stages: 
- Creating VM-templates to be used for deploying
- Deploying the templates to VMs
- Configuring the deployed VMs.

It uses Packer, Terraform and Ansible for deploying and configuring Virtual Machines (VMs), while using Vault for managing sensitive variables. It consists of two scripts, one for creating templates, and one for deploying the templates and configuring the deployed VMs. Its primary aim is to allow Blue and Red Teams to quickly spin up new lab environments.

### This project is split into two parts: first generating the VM templates using Packer, and then deploying the VMs using Terraform and Ansible.

See for the first part the `README-Packer.md` file, and for the second part the `README-Terraform.md` file.
