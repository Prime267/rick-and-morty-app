variable "cluster_name" {
  description = "Name of the Kubernetes cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version to use"
  type        = string
}

variable "region" {
  description = "The region where the cluster will be created"
  type        = string
}

variable "node_type" {
  description = "The type of nodes to use"
  type        = string
}

variable "node_count" {
  description = "Initial number of nodes to create in the node pool"
  type        = number
}

variable "min_nodes" {
  description = "Minimum number of nodes allowed in the node pool"
  type        = number
}

variable "max_nodes" {
  description = "Maximum number of nodes allowed in the node pool"
  type        = number
}

variable "vpc_id" {
  description = "The ID of the VPC to use"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the cluster"
  type        = list(string)
}
