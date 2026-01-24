############################################################
# Input variables for Terraform configuration
############################################################

variable "project" {
  type        = string
  description = "Logical project name used for tagging and naming."
  default     = "voice-ai-testing"
}

variable "environment" {
  type        = string
  description = "Deployment environment identifier (e.g., dev, staging, prod)."
  default     = "dev"
}

variable "aws_region" {
  type        = string
  description = "AWS region where infrastructure resources will be provisioned."
  default     = "us-east-1"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the primary VPC."
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type        = map(string)
  description = "Mapping of availability zones to CIDR blocks for public subnets."
  default = {
    "us-east-1a" = "10.0.1.0/24"
    "us-east-1b" = "10.0.2.0/24"
  }
}

variable "private_subnet_cidrs" {
  type        = map(string)
  description = "Mapping of availability zones to CIDR blocks for private subnets."
  default = {
    "us-east-1a" = "10.0.11.0/24"
    "us-east-1b" = "10.0.12.0/24"
  }
}

variable "availability_zones" {
  type        = list(string)
  description = "List of availability zones to distribute resources across."
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_name" {
  type        = string
  description = "Name of the default PostgreSQL database."
  default     = "voice_ai_testing"
}

variable "db_username" {
  type        = string
  description = "Master username for the PostgreSQL instance."
  default     = "voiceai_admin"
}

variable "db_password" {
  type        = string
  description = "Master password for the PostgreSQL instance."
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "Instance class for the PostgreSQL database."
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  type        = number
  description = "Allocated storage (in GB) for the PostgreSQL database."
  default     = 50
}

variable "db_backup_retention_period" {
  type        = number
  description = "Number of days to retain PostgreSQL backups."
  default     = 7
}

variable "db_multi_az" {
  type        = bool
  description = "Enable Multi-AZ deployment for PostgreSQL."
  default     = false
}

variable "redis_node_type" {
  type        = string
  description = "Instance class for ElastiCache nodes."
  default     = "cache.t3.micro"
}

variable "redis_engine_version" {
  type        = string
  description = "Redis engine version for the replication group."
  default     = "7.0"
}

variable "redis_port" {
  type        = number
  description = "Port for Redis communication."
  default     = 6379
}

variable "artifact_bucket_force_destroy" {
  type        = bool
  description = "Allow deletion of the artifacts bucket even when non-empty."
  default     = false
}

variable "log_bucket_expiration_days" {
  type        = number
  description = "Number of days before log objects are expired."
  default     = 365
}

variable "ecs_cluster_name" {
  type        = string
  description = "Optional override for ECS cluster name. Defaults to a derived value when null."
  default     = null
}

variable "ecs_task_cpu" {
  type        = string
  description = "CPU units for the ECS Fargate task definition."
  default     = "512"
}

variable "ecs_task_memory" {
  type        = string
  description = "Memory (in MiB) for the ECS Fargate task definition."
  default     = "1024"
}

variable "container_port" {
  type        = number
  description = "Container port exposed by the application."
  default     = 8000
}

variable "desired_task_count" {
  type        = number
  description = "Desired number of ECS tasks to run."
  default     = 2
}

variable "app_image" {
  type        = string
  description = "Container image for the application service."
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/voice-ai-testing:latest"
}

variable "alb_internal" {
  type        = bool
  description = "Whether the Application Load Balancer is internal (true) or internet-facing (false)."
  default     = false
}

variable "enable_ecs_autoscaling" {
  type        = bool
  description = "Enable Application Auto Scaling for the ECS service."
  default     = false
}

variable "ecs_autoscaling_min_capacity" {
  type        = number
  description = "Minimum number of ECS tasks when auto scaling is enabled."
  default     = 1
}

variable "ecs_autoscaling_max_capacity" {
  type        = number
  description = "Maximum number of ECS tasks when auto scaling is enabled."
  default     = 3
}

variable "ecs_autoscaling_target_cpu_utilization" {
  type        = number
  description = "Target CPU utilization percentage for ECS auto scaling."
  default     = 60
}
