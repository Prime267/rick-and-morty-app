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

provider "kubernetes" {
  host                   = module.lke_cluster.kubeconfig.0.host
  client_certificate     = base64decode(module.lke_cluster.kubeconfig.0.client_certificate)
  client_key             = base64decode(module.lke_cluster.kubeconfig.0.client_key)
  cluster_ca_certificate = base64decode(module.lke_cluster.kubeconfig.0.cluster_ca_certificate)
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
  allow_ips    = var.allow_ips  
}


# Kubernetes Namespace Creation
resource "kubernetes_namespace" "app_namespace" {
  metadata {
    name = var.app_namespace 
  }
  depends_on = [module.lke_cluster]
}

# Kubernetes Secret Creation (PostgreSQL Credentials)
resource "kubernetes_secret" "db_credentials" {
  metadata {
    name      = "rickmorty-db-creds"
    namespace = var.app_namespace 
  }

  type = "Opaque"

  data = {
    database-url = base64encode(
      "postgresql://${module.postgresql.username}:${module.postgresql.password}@${module.postgresql.host}:${module.postgresql.port}/${module.postgresql.database}"
    )
  }
  
  depends_on = [
    module.lke_cluster,
    module.postgresql
  ]
}
