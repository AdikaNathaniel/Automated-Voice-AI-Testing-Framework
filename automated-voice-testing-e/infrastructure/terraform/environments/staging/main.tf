############################################################
# Staging environment Terraform configuration
############################################################

module "staging" {
  source = "../.."

  project     = "voice-ai-testing"
  environment = "staging"

  aws_region = "us-east-1"

  db_name                     = "voice_ai_testing_staging"
  db_instance_class           = "db.t3.small"
  db_allocated_storage        = 20
  db_backup_retention_period  = 3
  db_multi_az                 = false
  artifact_bucket_force_destroy = true

  redis_node_type = "cache.t3.micro"

  app_image          = "123456789012.dkr.ecr.us-east-1.amazonaws.com/voice-ai-testing:staging"
  desired_task_count = 1
  alb_internal       = true
}
