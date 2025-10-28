output "host" {
  description = "Database host"
  value       = linode_database_postgresql_v2.rick_morty_db.host_primary
}

output "port" {
  description = "Database port"
  value       = linode_database_postgresql_v2.rick_morty_db.port
}

output "database" {
  description = "Database name"
  value       = var.db_name
}

output "username" {
  description = "Database username"
  value       = linode_database_postgresql_v2.rick_morty_db.root_username
}

output "password" {
  description = "Database password"
  value       = linode_database_postgresql_v2.rick_morty_db.root_password
  sensitive   = true
}
