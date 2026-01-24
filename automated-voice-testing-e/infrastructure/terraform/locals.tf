############################################################
# Local values shared across Terraform resources
############################################################

locals {
  name_prefix = "${var.project}-${var.environment}"

  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  public_subnet_keys        = sort(keys(var.public_subnet_cidrs))
  private_subnet_keys       = sort(keys(var.private_subnet_cidrs))
  primary_public_subnet_key = local.public_subnet_keys[0]
  ecs_cluster_name          = coalesce(var.ecs_cluster_name, "${local.name_prefix}-cluster")
  container_name            = "${local.name_prefix}-app"
  log_group_name            = "/voice-ai-testing/${var.environment}/app"
}
