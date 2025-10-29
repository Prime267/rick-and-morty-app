resource "linode_database_postgresql_v2" "rick_morty_db" {
  label     = "${var.cluster_name}-db"
  region    = var.region
  engine_id = "postgresql/18"
  type      = "g6-nanode-1"
  
  # Access configuration - your IP address
  allow_list = var.allow_ips

}
