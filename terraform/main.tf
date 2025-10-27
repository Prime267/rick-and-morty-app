terraform {
  required_providers {
    linode = {
      source = "linode/linode"
      version = "~> 2.0"
    }
  }
}

provider "linode" {
  token = var.linode_token
}

module "network" {
  source = "./modules/network"
  
  cluster_name = var.cluster_name
  region       = var.region
}

module "lke_cluster" {
  source = "./modules/lke-cluster"
  
  cluster_name       = var.cluster_name
  kubernetes_version = var.kubernetes_version
  region             = var.region
  node_type          = var.node_type
  node_count         = var.node_count
  min_nodes          = var.min_nodes
  max_nodes          = var.max_nodes
  vpc_id             = module.network.vpc_id
  tags               = var.tags
}

module "postgresql" {
  source = "./modules/postgresql"
  
  cluster_name = var.cluster_name
  region       = var.region
  db_name      = var.db_name
  db_username  = var.db_username
  db_password  = var.db_password
  allow_ips    = ["195.211.86.14/32"]  # Your home IP
}

module "kubernetes_resources" {
  source = "./modules/kubernetes-resources"
  
  cluster_name    = var.cluster_name
  kubeconfig      = module.lke_cluster.kubeconfig
  db_host         = module.postgresql.host
  db_port         = module.postgresql.port
  db_name         = module.postgresql.database
  db_username     = module.postgresql.username
  db_password     = module.postgresql.password
  
  depends_on = [
    module.lke_cluster,
    module.postgresql
  ]
}
