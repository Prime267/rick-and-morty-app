output "host" {
  description = "Database host"
  value       = linode_database_postgresql.rick_morty_db.host
}

output "port" {
  description = "Database port"
  value       = linode_database_postgresql.rick_morty_db.port
}

output "database" {
  description = "Database name"
  value       = linode_database_postgresql.rick_morty_db.database
}

output "username" {
  description = "Database username"
  value       = linode_database_postgresql.rick_morty_db.root_username
}

output "password" {
  description = "Database password"
  value       = linode_database_postgresql.rick_morty_db.root_password
  sensitive   = true
}
