variable "aws_region" {
  description = "The AWS region to deploy into"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "aivar-agent-waf"
}

variable "environment" {
  description = "The deployment environment"
  type        = string
  default     = "production"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "Name of the existing AWS key pair for SSH access"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to connect via SSH (Set this to your IP, e.g. x.x.x.x/32)"
  type        = string
  default     = "127.0.0.1/32"
}

variable "repository_url" {
  description = "GitHub repository URL to clone"
  type        = string
  default     = ""
}
