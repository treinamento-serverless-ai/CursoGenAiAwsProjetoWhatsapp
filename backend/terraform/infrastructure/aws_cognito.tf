# ============================================================================
# Amazon Cognito - User Authentication
# ============================================================================

# User Pool
resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-${var.environment}-users"

  # Desabilitar self-signup - apenas admin pode criar usuários
  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  # Login com email
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  # Política de senha
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = false
  }

  # Configurações de email
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-user-pool"
  }
}

# Grupo: Admin
resource "aws_cognito_user_group" "admin" {
  name         = "admin"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Administrators - can manage users and all system features"
  precedence   = 1
}

# Grupo: User
resource "aws_cognito_user_group" "user" {
  name         = "user"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Regular users - can use all system features except user management"
  precedence   = 2
}

# App Client para Web (Hosted UI)
resource "aws_cognito_user_pool_client" "web" {
  name         = "web-client"
  user_pool_id = aws_cognito_user_pool.main.id

  # OAuth flows
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]

  # Suporte para provedores de identidade
  supported_identity_providers = ["COGNITO"]

  # Callback URLs (construídas dinamicamente com base nas variáveis de controle)
  callback_urls = concat(
    var.cognito_allow_localhost_redirect ? ["http://localhost:4200/callback"] : [],
    var.cognito_allow_public_redirect ? [local.enable_custom_domain ? "https://${local.frontend_domain}/callback" : "http://${aws_s3_bucket.frontend.bucket}.s3-website-${var.aws_region}.amazonaws.com/callback"] : [],
  )

  logout_urls = concat(
    var.cognito_allow_localhost_redirect ? ["http://localhost:4200"] : [],
    var.cognito_allow_public_redirect ? [local.enable_custom_domain ? "https://${local.frontend_domain}" : "http://${aws_s3_bucket.frontend.bucket}.s3-website-${var.aws_region}.amazonaws.com"] : [],
  )

  # Configurações de token
  id_token_validity      = 60 # minutos
  access_token_validity  = 60 # minutos
  refresh_token_validity = 30 # dias

  token_validity_units {
    id_token      = "minutes"
    access_token  = "minutes"
    refresh_token = "days"
  }

  # Prevenir secret client (não necessário para SPA)
  generate_secret = false

  # Atributos que podem ser lidos
  read_attributes = [
    "email",
    "email_verified",
    "name",
  ]

  # Atributos que podem ser escritos
  write_attributes = [
    "email",
    "name",
  ]

  # Prevenir user existence errors
  prevent_user_existence_errors = "ENABLED"
}

# Domain para Hosted UI
resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.project_name}-${var.environment}-${random_id.unique_suffix.hex}"
  user_pool_id = aws_cognito_user_pool.main.id
}

# Authorizer para API Gateway
# Cognito authorizer is defined in openapi_agendente.yaml securitySchemes

# ============================================================================
# Criação de Usuários Iniciais
# ============================================================================

# Usuários Admin
resource "aws_cognito_user" "admins" {
  for_each = { for idx, user in var.cognito_initial_users.admins : idx => user }

  user_pool_id = aws_cognito_user_pool.main.id
  username     = each.value.email

  attributes = {
    email          = each.value.email
    email_verified = true
    name           = each.value.name
  }

  lifecycle {
    ignore_changes = [
      password,
      attributes["email_verified"]
    ]
  }
}

resource "aws_cognito_user_in_group" "admin_membership" {
  for_each = { for idx, user in var.cognito_initial_users.admins : idx => user }

  user_pool_id = aws_cognito_user_pool.main.id
  group_name   = aws_cognito_user_group.admin.name
  username     = aws_cognito_user.admins[each.key].username
}

# Usuários Regular
resource "aws_cognito_user" "regular_users" {
  for_each = { for idx, user in var.cognito_initial_users.regular_users : idx => user }

  user_pool_id = aws_cognito_user_pool.main.id
  username     = each.value.email

  attributes = {
    email          = each.value.email
    email_verified = true
    name           = each.value.name
  }

  lifecycle {
    ignore_changes = [
      password,
      attributes["email_verified"]
    ]
  }
}

resource "aws_cognito_user_in_group" "user_membership" {
  for_each = { for idx, user in var.cognito_initial_users.regular_users : idx => user }

  user_pool_id = aws_cognito_user_pool.main.id
  group_name   = aws_cognito_user_group.user.name
  username     = aws_cognito_user.regular_users[each.key].username
}

