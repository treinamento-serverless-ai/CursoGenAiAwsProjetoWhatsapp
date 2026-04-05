variable "aws_region" {
  type        = string
  description = "AWS region"
}

variable "custom_domain_name" {
  type        = string
  description = "Custom domain name for API Gateway and Frontend"
  default     = null
}

variable "cognito_admin_users" {
  type = list(object({
    name  = string
    email = string
  }))
  description = "List of admin users for Cognito"
  default     = []
}

variable "cognito_regular_users" {
  type = list(object({
    name  = string
    email = string
  }))
  description = "List of regular users for Cognito"
  default     = []
}
