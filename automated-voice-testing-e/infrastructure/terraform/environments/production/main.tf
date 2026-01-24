############################################################
# Production environment Terraform configuration
############################################################

module "production" {
  source = "../.."

  project     = "voice-ai-testing"
  environment = "production"

  aws_region = "us-east-1"
  availability_zones = [
    "us-east-1a",
    "us-east-1b",
    "us-east-1c",
  ]

  db_name                    = "voice_ai_testing_prod"
  db_instance_class          = "db.m6g.large"
  db_allocated_storage       = 100
  db_backup_retention_period = 14
  db_multi_az                = true

  redis_node_type = "cache.t3.medium"

  artifact_bucket_force_destroy = false

  app_image          = "123456789012.dkr.ecr.us-east-1.amazonaws.com/voice-ai-testing:production"
  desired_task_count = 3
  alb_internal       = false

  enable_ecs_autoscaling                 = true
  ecs_autoscaling_min_capacity           = 3
  ecs_autoscaling_max_capacity           = 10
  ecs_autoscaling_target_cpu_utilization = 55
}
