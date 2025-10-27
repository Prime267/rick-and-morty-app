provider "kubernetes" {
  host                   = yamldecode(base64decode(var.kubeconfig))["clusters"][0]["cluster"]["server"]
  cluster_ca_certificate = base64decode(yamldecode(base64decode(var.kubeconfig))["clusters"][0]["cluster"]["certificate-authority-data"])
  token                  = yamldecode(base64decode(var.kubeconfig))["users"][0]["user"]["token"]
}

provider "helm" {
  kubernetes {
    host                   = yamldecode(base64decode(var.kubeconfig))["clusters"][0]["cluster"]["server"]
    cluster_ca_certificate = base64decode(yamldecode(base64decode(var.kubeconfig))["clusters"][0]["cluster"]["certificate-authority-data"])
    token                  = yamldecode(base64decode(var.kubeconfig))["users"][0]["user"]["token"]
  }
}

resource "kubernetes_namespace" "rick_morty" {
  metadata {
    name = "rick-morty"
  }
}

# Creating secret for database
resource "kubernetes_secret" "db_credentials" {
  metadata {
    name      = "postgresql-credentials"
    namespace = kubernetes_namespace.rick_morty.metadata[0].name
  }
  
  data = {
    DATABASE_URL = "postgresql://${var.db_username}:${var.db_password}@${var.db_host}:${var.db_port}/${var.db_name}"
  }
}

# Installing NGINX Ingress Controller
resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  version    = "4.7.0"
  namespace  = "ingress-nginx"
  create_namespace = true

  set {
    name  = "controller.publishService.enabled"
    value = "true"
  }
}
