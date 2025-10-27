resource "linode_lke_cluster" "rick_morty_cluster" {
  label       = var.cluster_name
  k8s_version = var.kubernetes_version
  region      = var.region
  tags        = var.tags

  # Pool for worker nodes
  pool {
    type  = var.node_type
    count = var.node_count

    autoscaler {
      min = var.min_nodes
      max = var.max_nodes
    }
  }
}

# Export kubeconfig for further use
resource "local_file" "kubeconfig" {
  content         = base64decode(linode_lke_cluster.rick_morty_cluster.kubeconfig)
  filename        = "${path.module}/kubeconfig.yaml"
  file_permission = "0600"
}
