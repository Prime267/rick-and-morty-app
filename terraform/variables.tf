variable "linode_token" {
  description = "Linode API token"
  type        = string
  sensitive   = true
}

variable "cluster_name" {
  description = "Name of the Kubernetes cluster"
  type        = string
  default     = "rick-morty"
}

variable "kubernetes_version" {
  description = "Kubernetes version to use"
  type        = string
  default     = "1.27"
}

variable "region" {
  description = "The region where the cluster will be created"
  type        = string
  default     = "eu-central"
}

variable "node_type" {
  description = "The type of nodes to use"
  type        = string
  default     = "g6-standard-2"  # 2 CPU, 4GB RAM
}

variable "node_count" {
  description = "Initial number of nodes to create in the node pool"
  type        = number
  default     = 2
}

variable "min_nodes" {
  description = "Minimum number of nodes allowed in the node pool"
  type        = number
  default     = 1
}

variable "max_nodes" {
  description = "Maximum number of nodes allowed in the node pool"
  type        = number
  default     = 3
}

variable "tags" {
  description = "Tags to apply to the cluster"
  type        = list(string)
  default     = ["production", "rick-morty-api"]
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "rickmorty"
}

variable "db_username" {
  description = "PostgreSQL username"
  type        = string
  default     = "rickmorty"
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}