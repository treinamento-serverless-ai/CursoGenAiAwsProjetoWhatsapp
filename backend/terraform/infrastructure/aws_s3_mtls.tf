# ============================================================================
# S3 Bucket - mTLS Truststore (somente quando custom domain está habilitado)
# ============================================================================

resource "aws_s3_bucket" "mtls_truststore" {
  count         = local.enable_custom_domain ? 1 : 0
  bucket        = "${var.project_name}-${var.environment}-mtls-truststore-${random_id.unique_suffix.hex}"
  force_destroy = true

  tags = {
    Name = "${var.project_name}-${var.environment}-mtls-truststore"
  }
}

resource "aws_s3_bucket_versioning" "mtls_truststore" {
  count  = local.enable_custom_domain ? 1 : 0
  bucket = aws_s3_bucket.mtls_truststore[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "mtls_truststore" {
  count  = local.enable_custom_domain ? 1 : 0
  bucket = aws_s3_bucket.mtls_truststore[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ============================================================================
# Upload do certificado Meta CA para S3
# ============================================================================
#
# O certificado Meta CA (meta-outbound-api-ca-2025-12.pem) deve ser baixado
# manualmente a partir da documentação oficial da Meta:
# https://developers.facebook.com/docs/graph-api/webhooks/getting-started/#downloadable-root-certificate
#
# Coloque o .pem na pasta certs/ do environment (ex: environments/dev/certs/)
# e informe o caminho via variável meta_ca_cert_path.
# ============================================================================

resource "aws_s3_object" "mtls_truststore_certificate" {
  count   = local.enable_custom_domain ? 1 : 0
  bucket  = aws_s3_bucket.mtls_truststore[0].id
  key     = basename(var.meta_ca_cert_path)
  source  = var.meta_ca_cert_path
  etag    = filemd5(var.meta_ca_cert_path)

  depends_on = [aws_s3_bucket_versioning.mtls_truststore]

  tags = {
    Name        = "Meta CA mTLS Truststore"
    Description = "Meta Outbound API CA para mTLS de Webhooks WhatsApp"
  }
}

# Outputs
output "mtls_truststore_uri" {
  value       = local.enable_custom_domain ? "s3://${aws_s3_bucket.mtls_truststore[0].id}/${aws_s3_object.mtls_truststore_certificate[0].key}" : null
  description = "URI do truststore no S3 para configuração mTLS no API Gateway"
}

output "mtls_truststore_version" {
  value       = local.enable_custom_domain ? aws_s3_object.mtls_truststore_certificate[0].version_id : null
  description = "Versão do truststore no S3"
}
