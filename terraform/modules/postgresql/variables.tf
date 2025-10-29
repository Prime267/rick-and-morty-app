variable "cluster_name" {
  description = "Name of the Kubernetes cluster"
  type        = string
}

variable "region" {
  description = "The region where the database will be created"
  type        = string
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
}

variable "db_username" {
  description = "PostgreSQL username"
  type        = string
}

variable "allow_ips" {
  description = "List of IPs allowed to connect to the database"
  type        = list(string)
  default     = []
}
