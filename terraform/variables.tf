variable "resource_group_name" {
  type        = string
  description = "Name of the resource group."
}

variable "location" {
  type        = string
  description = "Azure region where the resources will be created."
  default     = "Central India"
}

variable "vm_size" {
  type        = string
  description = "Size of the Virtual Machine."
  default     = "Standard_B2s" 
}

variable "admin_username" {
  type        = string
  description = "Username for the Virtual Machine."
}

variable "admin_password" {
  type        = string
  description = "Password for the Virtual Machine."
  sensitive   = true
}
