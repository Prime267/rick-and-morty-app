# Create namespace for NGINX Ingress Controller
resource "kubernetes_namespace" "ingress_nginx" {
  metadata {
    name = "ingress-nginx"
    labels = {
      "app.kubernetes.io/name"      = "ingress-nginx"
      "app.kubernetes.io/instance"  = "ingress-nginx"
    }
  }
  depends_on = [module.lke_cluster]
}

# Deploy NGINX Ingress Controller using Helm
resource "helm_release" "nginx_ingress" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  version    = "4.11.3"  # Latest stable version (Dec 2024)
  namespace  = kubernetes_namespace.ingress_nginx.metadata[0].name
  
  # Deployment settings
  wait             = true
  create_namespace = false
  timeout          = 600
  cleanup_on_fail  = true
  force_update     = true
  
  # Chart values configuration
  values = [
    yamlencode({
      controller = {
        # LoadBalancer service configuration
        service = {
          type = "LoadBalancer"
          externalTrafficPolicy = "Local"  # Preserve client IP
          
          # Linode NodeBalancer specific annotations
          annotations = {
            "service.beta.kubernetes.io/linode-loadbalancer-throttle" = "4"
          }
        }
        
        # Ingress Class configuration
        ingressClass = "nginx"
        ingressClassResource = {
          name            = "nginx"
          enabled         = true
          default         = true  # Set as default ingress class
          controllerValue = "k8s.io/ingress-nginx"
        }
        
        # Enable Prometheus metrics
        metrics = {
          enabled = true
          serviceMonitor = {
            enabled = false  # Enable if Prometheus Operator is installed
          }
        }
        
        # Resource limits for production
        resources = {
          limits = {
            cpu    = "500m"
            memory = "512Mi"
          }
          requests = {
            cpu    = "250m"
            memory = "256Mi"
          }
        }
        
        # Horizontal Pod Autoscaler configuration
        autoscaling = {
          enabled                           = true
          minReplicas                      = 1
          maxReplicas                      = 2
          targetCPUUtilizationPercentage  = 80
          targetMemoryUtilizationPercentage = 80
        }
        
        # Security context for pods
        podSecurityContext = {
          runAsNonRoot = true
          runAsUser    = 101
          runAsGroup   = 101
          fsGroup      = 101
        }
        
        # Container security settings
        containerSecurityContext = {
          allowPrivilegeEscalation = false
          capabilities = {
            drop = ["ALL"]
            add  = ["NET_BIND_SERVICE"]
          }
          readOnlyRootFilesystem = false
          runAsNonRoot          = true
          runAsUser             = 101
        }
        
        # Enable admission webhooks for validation
        admissionWebhooks = {
          enabled = true
          failurePolicy = "Fail"
          port = 8443
          
          patch = {
            enabled = true
            image = {
              registry = "registry.k8s.io"
              image    = "ingress-nginx/kube-webhook-certgen"
              tag      = "v1.4.3"
            }
          }
        }
        
        # NGINX configuration parameters
        config = {
          # Enhanced logging format
          "log-format-upstream" = "$remote_addr - $remote_user [$time_local] \"$request\" $status $body_bytes_sent \"$http_referer\" \"$http_user_agent\" $request_length $request_time [$proxy_upstream_name] [$proxy_alternative_upstream_name] $upstream_addr $upstream_response_length $upstream_response_time $upstream_status $req_id"
          
          # Header forwarding
          "use-forwarded-headers" = "true"
          "compute-full-forwarded-for" = "true"
          "use-proxy-protocol" = "false"
          
          # SSL/TLS configuration
          "ssl-protocols" = "TLSv1.2 TLSv1.3"
          
          # Performance tuning
          "keep-alive-requests" = "10000"
          "upstream-keepalive-connections" = "320"
          "upstream-keepalive-requests" = "10000"
        }
        
        # Pod anti-affinity for high availability
        affinity = {
          podAntiAffinity = {
            preferredDuringSchedulingIgnoredDuringExecution = [
              {
                weight = 100
                podAffinityTerm = {
                  labelSelector = {
                    matchExpressions = [
                      {
                        key      = "app.kubernetes.io/name"
                        operator = "In"
                        values   = ["ingress-nginx"]
                      }
                    ]
                  }
                  topologyKey = "kubernetes.io/hostname"
                }
              }
            ]
          }
        }
      }
      
      # Default backend configuration (optional)
      defaultBackend = {
        enabled = false  # Enable if you want custom 404 pages
      }
    })
  ]
  
  depends_on = [
    module.lke_cluster,
    kubernetes_namespace.ingress_nginx
  ]
}

# Data source to get LoadBalancer details
data "kubernetes_service" "nginx_ingress" {
  metadata {
    name      = "ingress-nginx-controller"
    namespace = kubernetes_namespace.ingress_nginx.metadata[0].name
  }
  
  depends_on = [helm_release.nginx_ingress]
}