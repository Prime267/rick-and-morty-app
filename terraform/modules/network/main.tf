resource "linode_vpc" "rick_morty_vpc" {
  label       = "${var.cluster_name}-vpc"
  region      = var.region
  description = "VPC for Rick and Morty API project"
}

resource "linode_vpc_subnet" "rick_morty_subnet" {
  vpc_id     = linode_vpc.rick_morty_vpc.id
  label      = "${var.cluster_name}-subnet"
  ipv4       = "10.0.0.0/24"
}
