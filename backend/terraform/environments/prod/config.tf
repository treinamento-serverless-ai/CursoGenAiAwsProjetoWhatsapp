# ============================================================================
# Terraform, Provider and Backend Configuration
# ============================================================================

terraform {
  required_version = ">= 1.6.0"

  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

# Provider padrão
provider "aws" {
  region = var.aws_region
}

# Provider adicional para us-east-1 (necessário para certificados CloudFront)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
