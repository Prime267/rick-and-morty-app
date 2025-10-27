output "vpc_id" {
  description = "The ID of the VPC"
  value       = linode_vpc.rick_morty_vpc.id
}

output "subnet_id" {
  description = "The ID of the subnet"
  value       = linode_vpc_subnet.rick_morty_subnet.id
}
