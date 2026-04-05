# ============================================================================
# Custom Domain Names - API Gateway e Frontend
# ============================================================================

# Data sources
data "aws_region" "current" {}

# Locals para construir subdomínios
locals {
  enable_custom_domain = var.custom_domain_name != null
  
  # Subdomínios: dev.barbearia-silva.serverlessai.click
  frontend_domain  = local.enable_custom_domain ? "${var.environment}.${var.project_name}.${var.custom_domain_name}" : null
  api_domain       = local.enable_custom_domain ? "api.${var.environment}.${var.project_name}.${var.custom_domain_name}" : null
  whatsapp_domain  = local.enable_custom_domain ? "whatsapp.${var.environment}.${var.project_name}.${var.custom_domain_name}" : null
}

# ============================================================================
# Route 53 - Hosted Zone Lookup
# ============================================================================

data "aws_route53_zone" "main" {
  count = local.enable_custom_domain ? 1 : 0
  
  name         = var.custom_domain_name
  private_zone = false
}

# ============================================================================
# ACM Certificate - API Gateway
# ============================================================================

resource "aws_acm_certificate" "api" {
  count = local.enable_custom_domain ? 1 : 0
  
  domain_name       = local.api_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-api-certificate"
  }
}

# DNS validation records
resource "aws_route53_record" "api_cert_validation" {
  for_each = local.enable_custom_domain ? {
    for dvo in aws_acm_certificate.api[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.main[0].zone_id
}

# Certificate validation
resource "aws_acm_certificate_validation" "api" {
  count = local.enable_custom_domain ? 1 : 0
  
  certificate_arn         = aws_acm_certificate.api[0].arn
  validation_record_fqdns = [for record in aws_route53_record.api_cert_validation : record.fqdn]
}

# ============================================================================
# API Gateway - Custom Domain Name with mTLS (WhatsApp)
# ============================================================================

resource "aws_acm_certificate" "whatsapp" {
  count = local.enable_custom_domain ? 1 : 0
  
  domain_name       = local.whatsapp_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-whatsapp-certificate"
  }
}

# DNS validation records for WhatsApp
resource "aws_route53_record" "whatsapp_cert_validation" {
  for_each = local.enable_custom_domain ? {
    for dvo in aws_acm_certificate.whatsapp[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.main[0].zone_id
}

# Certificate validation for WhatsApp
resource "aws_acm_certificate_validation" "whatsapp" {
  count = local.enable_custom_domain ? 1 : 0
  
  certificate_arn         = aws_acm_certificate.whatsapp[0].arn
  validation_record_fqdns = [for record in aws_route53_record.whatsapp_cert_validation : record.fqdn]
}

# Custom domain for WhatsApp with mTLS
resource "aws_api_gateway_domain_name" "whatsapp" {
  count = local.enable_custom_domain ? 1 : 0
  
  domain_name              = local.whatsapp_domain
  regional_certificate_arn = aws_acm_certificate_validation.whatsapp[0].certificate_arn
  security_policy          = "TLS_1_2"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  mutual_tls_authentication {
    truststore_uri     = "s3://${aws_s3_bucket.mtls_truststore[0].id}/${aws_s3_object.mtls_truststore_certificate[0].key}"
    truststore_version = aws_s3_object.mtls_truststore_certificate[0].version_id
  }

  depends_on = [aws_acm_certificate_validation.whatsapp]

  tags = {
    Name = "${var.project_name}-${var.environment}-whatsapp-domain"
  }
}

# Base path mapping for WhatsApp (root path)
resource "aws_api_gateway_base_path_mapping" "whatsapp" {
  count = local.enable_custom_domain ? 1 : 0
  
  api_id      = aws_api_gateway_rest_api.whatsapp.id
  stage_name  = aws_api_gateway_stage.whatsapp.stage_name
  domain_name = aws_api_gateway_domain_name.whatsapp[0].domain_name
}

# Route 53 record for WhatsApp
resource "aws_route53_record" "whatsapp" {
  count = local.enable_custom_domain ? 1 : 0
  
  zone_id = data.aws_route53_zone.main[0].zone_id
  name    = local.whatsapp_domain
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.whatsapp[0].regional_domain_name
    zone_id                = aws_api_gateway_domain_name.whatsapp[0].regional_zone_id
    evaluate_target_health = false
  }
}

# ============================================================================
# API Gateway - Custom Domain Name (Admin API - sem mTLS)
# ============================================================================

resource "aws_api_gateway_domain_name" "api" {
  count = local.enable_custom_domain ? 1 : 0
  
  domain_name              = local.api_domain
  regional_certificate_arn = aws_acm_certificate_validation.api[0].certificate_arn
  security_policy          = "TLS_1_2"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  depends_on = [aws_acm_certificate_validation.api]

  tags = {
    Name = "${var.project_name}-${var.environment}-api-domain"
  }
}

# Base path mapping
resource "aws_api_gateway_base_path_mapping" "api" {
  count = local.enable_custom_domain ? 1 : 0
  
  api_id      = aws_api_gateway_rest_api.main.id
  stage_name  = aws_api_gateway_stage.main.stage_name
  domain_name = aws_api_gateway_domain_name.api[0].domain_name
}

# Route 53 record for API
resource "aws_route53_record" "api" {
  count = local.enable_custom_domain ? 1 : 0
  
  zone_id = data.aws_route53_zone.main[0].zone_id
  name    = local.api_domain
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.api[0].regional_domain_name
    zone_id                = aws_api_gateway_domain_name.api[0].regional_zone_id
    evaluate_target_health = false
  }
}

# ============================================================================
# ACM Certificate - Frontend (CloudFront)
# ============================================================================

# CloudFront requires certificate in us-east-1
resource "aws_acm_certificate" "frontend" {
  count = local.enable_custom_domain ? 1 : 0
  
  provider = aws.us_east_1
  
  domain_name       = local.frontend_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-frontend-certificate"
  }
}

# DNS validation records for frontend
resource "aws_route53_record" "frontend_cert_validation" {
  for_each = local.enable_custom_domain ? {
    for dvo in aws_acm_certificate.frontend[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.main[0].zone_id
}

# Certificate validation for frontend
resource "aws_acm_certificate_validation" "frontend" {
  count = local.enable_custom_domain ? 1 : 0
  
  provider = aws.us_east_1
  
  certificate_arn         = aws_acm_certificate.frontend[0].arn
  validation_record_fqdns = [for record in aws_route53_record.frontend_cert_validation : record.fqdn]
}

# ============================================================================
# CloudFront Distribution - Frontend
# ============================================================================

resource "aws_cloudfront_origin_access_control" "frontend" {
  count = local.enable_custom_domain ? 1 : 0

  name                              = "${var.project_name}-${var.environment}-frontend-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "frontend" {
  count = local.enable_custom_domain ? 1 : 0
  
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  aliases             = [local.frontend_domain]

  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.frontend.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend[0].id
  }

  # SPA: redireciona 403/404 para index.html (Angular router)
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.frontend.id}"

    cache_policy_id = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad" # CachingDisabled

    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.frontend[0].certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-frontend-cdn"
  }
}

# Route 53 record for Frontend
resource "aws_route53_record" "frontend" {
  count = local.enable_custom_domain ? 1 : 0
  
  zone_id = data.aws_route53_zone.main[0].zone_id
  name    = local.frontend_domain
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend[0].domain_name
    zone_id                = aws_cloudfront_distribution.frontend[0].hosted_zone_id
    evaluate_target_health = false
  }
}

# ============================================================================
# Outputs
# ============================================================================

output "custom_domain_enabled" {
  value       = local.enable_custom_domain
  description = "Indica se custom domain está habilitado"
}

output "api_custom_domain" {
  value       = local.enable_custom_domain ? "https://${local.api_domain}" : null
  description = "URL customizada da API (com mTLS habilitado)"
}

output "frontend_custom_domain" {
  value       = local.enable_custom_domain ? "https://${local.frontend_domain}" : null
  description = "URL customizada do Frontend (via CloudFront)"
}

output "webhook_custom_url" {
  value       = local.enable_custom_domain ? "https://${local.whatsapp_domain}" : null
  description = "URL customizada do webhook para configurar na Meta (raiz do domínio)"
}
