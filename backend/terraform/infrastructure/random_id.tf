# ============================================================================
# Random ID Generator - Para recursos que exigem nomes únicos globalmente
# ============================================================================

resource "random_id" "unique_suffix" {
  byte_length = 4
}

# Output para referência
output "unique_suffix" {
  value       = random_id.unique_suffix.hex
  description = "Sufixo único gerado para recursos que exigem nomes globalmente únicos"
}
