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
