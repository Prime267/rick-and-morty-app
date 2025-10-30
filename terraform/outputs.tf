output "cluster_id" {
  description = "ID of the LKE cluster"
  value       = module.lke_cluster.cluster_id
}

output "api_endpoints" {
  description = "The API endpoints for the cluster"
  value       = module.lke_cluster.api_endpoints
}

output "cluster_status" {
  description = "Status of the cluster"
  value       = module.lke_cluster.status
}

output "kubeconfig_path" {
  description = "Path to the kubeconfig file"
  value       = module.lke_cluster.kubeconfig_path
}

output "database_host" {
  description = "PostgreSQL database host"
  value       = module.postgresql.host
}

output "database_port" {
  description = "PostgreSQL database port"
  value       = module.postgresql.port
}


# Outputs for CI/CD pipeline to use
output "kubeconfig" {
  value       = module.lke_cluster.kubeconfig
  sensitive   = true
  description = "Kubeconfig for the Kubernetes cluster (base64 encoded)"
}

output "db_port" {
  value       = module.postgresql.port
  description = "PostgreSQL database port"
}

output "db_name" {
  value       = module.postgresql.database
  description = "PostgreSQL database name"
}

output "db_username" {
  value       = module.postgresql.username
  sensitive = true
  description = "PostgreSQL database username"
}

output "db_password" {
  value       = module.postgresql.password
  sensitive   = true
  description = "PostgreSQL database password"
}

# # New output to get Kubernetes node IPs for database access
# output "node_ips" {
#   value       = module.lke_cluster.node_ips
#   description = "External IP addresses of Kubernetes nodes"
# }
