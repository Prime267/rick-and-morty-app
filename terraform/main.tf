terraform {
  required_providers {
    linode = {
      source  = "linode/linode"
      version = "~> 2.0"
    }
  }
  
  backend "remote" {
    hostname     = "app.terraform.io"
    organization = "akamai_rick_morty"
    
    workspaces {
      name = "rick_morty_workspace"
    }
  }
}

provider "linode" {
  token = var.linode_token
}

module "lke_cluster" {
  source = "./modules/lke-cluster"
  
  providers = {
    linode = linode
  }
  
  cluster_name       = var.cluster_name
  kubernetes_version = var.kubernetes_version
  region             = var.region
  node_type          = var.node_type
  node_count         = var.node_count
  min_nodes          = var.min_nodes
  max_nodes          = var.max_nodes
  tags               = var.tags
}

module "postgresql" {
  source = "./modules/postgresql"
  
  providers = {
    linode = linode
  }
  
  cluster_name = var.cluster_name
  region       = var.region
  db_name      = var.db_name
  db_username  = var.db_username
  db_password  = var.db_password
  allow_ips    = ["195.211.86.14/32"]  # Your home IP
}
