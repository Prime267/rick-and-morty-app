output "cluster_id" {
  description = "ID of the LKE cluster"
  value       = linode_lke_cluster.rick_morty_cluster.id
}

output "api_endpoints" {
  description = "The API endpoints for the cluster"
  value       = linode_lke_cluster.rick_morty_cluster.api_endpoints
}

output "status" {
  description = "Status of the cluster"
  value       = linode_lke_cluster.rick_morty_cluster.status
}

output "kubeconfig" {
  description = "Kubeconfig for the cluster (base64 encoded)"
  value       = linode_lke_cluster.rick_morty_cluster.kubeconfig
  sensitive   = true
}

output "kubeconfig_path" {
  description = "Path to the kubeconfig file"
  value       = local_file.kubeconfig.filename
}

# New output to get node IPs
# output "node_ips" {
#   description = "External IP addresses of Kubernetes nodes"
#   value       = flatten([
#     for pool in linode_lke_cluster.rick_morty_cluster.pool : [
#       for node in pool.nodes : node.ipv4
#     ]
#   ])
# }
