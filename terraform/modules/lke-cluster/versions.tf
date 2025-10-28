terraform {
  required_providers {
    linode = {
      source = "linode/linode"
    }
    local = {
      source = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}
