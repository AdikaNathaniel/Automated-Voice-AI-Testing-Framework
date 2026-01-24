############################################################
# Shared outputs for Terraform consumers
############################################################

output "project" {
  description = "Logical project name applied to infrastructure resources."
  value       = var.project
}

output "environment" {
  description = "Deployment environment for the infrastructure."
  value       = var.environment
}

output "region" {
  description = "AWS region where the infrastructure is deployed."
  value       = var.aws_region
}

output "name_prefix" {
  description = "Standardized prefix for resource naming."
  value       = local.name_prefix
}
