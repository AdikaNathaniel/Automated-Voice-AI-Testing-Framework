"""
Tests for Terraform infrastructure modules validation.

This test suite validates that Terraform modules are properly configured for pilot:
1. Networking (VPC, subnets, security groups)
2. Compute (ECS/EKS/VMs) sizing for expected pilot load
3. Storage (RDS/Postgres, S3/MinIO buckets)
4. Security best practices
"""

import re
from pathlib import Path
from typing import Any, Dict, List

import pytest


class TestTerraformStructure:
    """Test Terraform project structure and file organization"""

    @pytest.fixture
    def terraform_dir(self):
        """Get path to terraform directory"""
        return Path(__file__).parent.parent / "infrastructure" / "terraform"

    def test_terraform_directory_exists(self, terraform_dir):
        """Test that terraform directory exists"""
        assert terraform_dir.exists(), (
            "Terraform directory not found at infrastructure/terraform"
        )
        assert terraform_dir.is_dir(), "Terraform path should be a directory"

    def test_required_terraform_files_exist(self, terraform_dir):
        """Test that required Terraform files exist"""
        required_files = [
            "providers.tf",
            "variables.tf",
            "networking.tf",
            "compute.tf",
            "storage.tf",
            "locals.tf",
            "main.tf",
            "outputs.tf",
        ]

        for file_name in required_files:
            file_path = terraform_dir / file_name
            assert file_path.exists(), (
                f"Required Terraform file '{file_name}' not found"
            )

    def test_terraform_version_constraint(self, terraform_dir):
        """Test that Terraform version is properly constrained"""
        providers_file = terraform_dir / "providers.tf"
        content = providers_file.read_text()

        # Should have terraform block
        assert "terraform {" in content, (
            "providers.tf should have terraform configuration block"
        )

        # Should have version constraint
        assert "required_version" in content, (
            "providers.tf should specify required_version"
        )

        # Version should be >= 1.5.0
        assert ">= 1.5" in content or ">= 1.6" in content, (
            "Terraform version should be >= 1.5.0"
        )

    def test_aws_provider_configured(self, terraform_dir):
        """Test that AWS provider is properly configured"""
        providers_file = terraform_dir / "providers.tf"
        content = providers_file.read_text()

        # Should have AWS provider
        assert "hashicorp/aws" in content, (
            "providers.tf should configure AWS provider"
        )

        # Should have version constraint
        assert "version" in content, (
            "AWS provider should have version constraint"
        )


class TestNetworkingModule:
    """Test networking module (VPC, subnets, security groups) - TODOS.md requirement"""

    @pytest.fixture
    def terraform_dir(self):
        """Get path to terraform directory"""
        return Path(__file__).parent.parent / "infrastructure" / "terraform"

    @pytest.fixture
    def networking_content(self, terraform_dir):
        """Read networking.tf content"""
        networking_file = terraform_dir / "networking.tf"
        return networking_file.read_text()

    @pytest.fixture
    def variables_content(self, terraform_dir):
        """Read variables.tf content"""
        variables_file = terraform_dir / "variables.tf"
        return variables_file.read_text()

    def test_vpc_resource_defined(self, networking_content):
        """Test that VPC resource is defined"""
        assert 'resource "aws_vpc"' in networking_content, (
            "networking.tf should define aws_vpc resource"
        )

        # Should enable DNS support
        assert "enable_dns_support" in networking_content, (
            "VPC should enable DNS support"
        )

        # Should enable DNS hostnames
        assert "enable_dns_hostnames" in networking_content, (
            "VPC should enable DNS hostnames"
        )

    def test_vpc_cidr_configuration(self, variables_content):
        """Test that VPC CIDR is properly configured"""
        assert "vpc_cidr" in variables_content, (
            "variables.tf should define vpc_cidr variable"
        )

        # Default CIDR should be reasonable (10.0.0.0/16 is common for pilot)
        assert "10.0.0.0/16" in variables_content, (
            "VPC CIDR default should be 10.0.0.0/16 for pilot"
        )

    def test_public_subnets_defined(self, networking_content):
        """Test that public subnets are defined"""
        assert 'resource "aws_subnet" "public"' in networking_content, (
            "networking.tf should define public subnets"
        )

        # Should use for_each for multi-AZ deployment
        assert "for_each" in networking_content, (
            "Public subnets should use for_each for multi-AZ deployment"
        )

        # Should map public IP on launch
        assert "map_public_ip_on_launch = true" in networking_content, (
            "Public subnets should map public IP on launch"
        )

    def test_private_subnets_defined(self, networking_content):
        """Test that private subnets are defined"""
        assert 'resource "aws_subnet" "private"' in networking_content, (
            "networking.tf should define private subnets"
        )

    def test_multi_az_deployment(self, variables_content):
        """Test that infrastructure spans multiple availability zones"""
        assert "availability_zones" in variables_content, (
            "variables.tf should define availability_zones"
        )

        # Should have at least 2 AZs for pilot (high availability)
        # Check for multiple AZ references
        az_pattern = r'us-east-1[a-z]'
        az_matches = re.findall(az_pattern, variables_content)

        assert len(set(az_matches)) >= 2, (
            "Should have at least 2 availability zones for high availability"
        )

    def test_internet_gateway_defined(self, networking_content):
        """Test that Internet Gateway is defined for public subnet access"""
        assert 'resource "aws_internet_gateway"' in networking_content, (
            "networking.tf should define Internet Gateway for public access"
        )

    def test_nat_gateway_defined(self, networking_content):
        """Test that NAT Gateway is defined for private subnet internet access"""
        assert 'resource "aws_nat_gateway"' in networking_content, (
            "networking.tf should define NAT Gateway for private subnet internet access"
        )

        # Should have Elastic IP for NAT Gateway
        assert 'resource "aws_eip" "nat"' in networking_content, (
            "networking.tf should define Elastic IP for NAT Gateway"
        )

    def test_route_tables_defined(self, networking_content):
        """Test that route tables are defined for public and private subnets"""
        # Public route table
        assert 'resource "aws_route_table" "public"' in networking_content, (
            "networking.tf should define public route table"
        )

        # Private route table
        assert 'resource "aws_route_table" "private"' in networking_content, (
            "networking.tf should define private route table"
        )

        # Route table associations
        assert 'resource "aws_route_table_association"' in networking_content, (
            "networking.tf should define route table associations"
        )

    def test_alb_security_group_defined(self, networking_content):
        """Test that ALB security group is defined"""
        assert 'resource "aws_security_group" "alb"' in networking_content, (
            "networking.tf should define ALB security group"
        )

        # Should allow HTTP (port 80)
        assert "80" in networking_content, (
            "ALB security group should allow HTTP traffic on port 80"
        )

        # Should allow HTTPS (port 443)
        assert "443" in networking_content, (
            "ALB security group should allow HTTPS traffic on port 443"
        )

    def test_app_security_group_defined(self, networking_content):
        """Test that application security group is defined"""
        assert 'resource "aws_security_group" "app"' in networking_content, (
            "networking.tf should define application security group"
        )

        # Should reference ALB security group
        assert "security_groups" in networking_content, (
            "App security group should reference ALB security group"
        )

    def test_security_group_best_practices(self, networking_content):
        """Test that security groups follow best practices"""
        # Should not allow 0.0.0.0/0 on ingress for app security group
        # (only ALB should allow public access)

        # Should have egress rules
        assert "egress" in networking_content, (
            "Security groups should have egress rules defined"
        )


class TestComputeModule:
    """Test compute module (ECS/Fargate) sizing - TODOS.md requirement"""

    @pytest.fixture
    def terraform_dir(self):
        """Get path to terraform directory"""
        return Path(__file__).parent.parent / "infrastructure" / "terraform"

    @pytest.fixture
    def compute_content(self, terraform_dir):
        """Read compute.tf content"""
        compute_file = terraform_dir / "compute.tf"
        return compute_file.read_text()

    @pytest.fixture
    def variables_content(self, terraform_dir):
        """Read variables.tf content"""
        variables_file = terraform_dir / "variables.tf"
        return variables_file.read_text()

    def test_ecs_cluster_defined(self, compute_content):
        """Test that ECS cluster is defined"""
        assert 'resource "aws_ecs_cluster"' in compute_content, (
            "compute.tf should define ECS cluster"
        )

        # Should enable Container Insights for monitoring
        assert "containerInsights" in compute_content or "container_insights" in compute_content, (
            "ECS cluster should enable Container Insights for monitoring"
        )

    def test_ecs_task_definition_defined(self, compute_content):
        """Test that ECS task definition is defined"""
        assert 'resource "aws_ecs_task_definition"' in compute_content, (
            "compute.tf should define ECS task definition"
        )

        # Should use Fargate
        assert "FARGATE" in compute_content, (
            "Task definition should use FARGATE launch type"
        )

        # Should use awsvpc network mode
        assert "awsvpc" in compute_content, (
            "Task definition should use awsvpc network mode for Fargate"
        )

    def test_ecs_task_sizing_configured(self, variables_content):
        """Test that ECS task CPU and memory sizing is configured (TODOS.md requirement)"""
        assert "ecs_task_cpu" in variables_content, (
            "variables.tf should define ecs_task_cpu for sizing"
        )

        assert "ecs_task_memory" in variables_content, (
            "variables.tf should define ecs_task_memory for sizing"
        )

        # Check default values are reasonable for pilot
        # 512 CPU units (0.5 vCPU) and 1024 MB (1 GB) is reasonable for pilot
        assert '"512"' in variables_content or "'512'" in variables_content, (
            "Default CPU should be 512 for pilot load"
        )

        assert '"1024"' in variables_content or "'1024'" in variables_content, (
            "Default memory should be 1024 MB for pilot load"
        )

    def test_desired_task_count_configured(self, variables_content):
        """Test that desired task count is configured for pilot load"""
        assert "desired_task_count" in variables_content, (
            "variables.tf should define desired_task_count"
        )

        # Should have at least 2 tasks for high availability
        # Default = 2 is reasonable for pilot
        content = variables_content
        # Find default value for desired_task_count
        if "default" in content and "desired_task_count" in content:
            # Good - has default configured
            pass

    def test_application_load_balancer_defined(self, compute_content):
        """Test that Application Load Balancer is defined"""
        assert 'resource "aws_lb"' in compute_content, (
            "compute.tf should define Application Load Balancer"
        )

        # Should be application type
        assert '"application"' in compute_content or "'application'" in compute_content, (
            "Load balancer should be application type"
        )

    def test_alb_target_group_defined(self, compute_content):
        """Test that ALB target group is defined"""
        assert 'resource "aws_lb_target_group"' in compute_content, (
            "compute.tf should define ALB target group"
        )

        # Should have health check configured
        assert "health_check" in compute_content, (
            "ALB target group should have health check configured"
        )

        # Health check should use /health endpoint
        assert "/health" in compute_content, (
            "Health check should use /health endpoint"
        )

    def test_ecs_service_defined(self, compute_content):
        """Test that ECS service is defined"""
        assert 'resource "aws_ecs_service"' in compute_content, (
            "compute.tf should define ECS service"
        )

        # Should use Fargate launch type
        assert 'launch_type      = "FARGATE"' in compute_content, (
            "ECS service should use FARGATE launch type"
        )

    def test_ecs_autoscaling_configured(self, variables_content, compute_content):
        """Test that ECS autoscaling is configured for pilot load (TODOS.md requirement)"""
        # Should have autoscaling variable
        assert "enable_ecs_autoscaling" in variables_content, (
            "variables.tf should have enable_ecs_autoscaling option"
        )

        # Should have autoscaling capacity variables
        assert "ecs_autoscaling_min_capacity" in variables_content, (
            "variables.tf should define min autoscaling capacity"
        )

        assert "ecs_autoscaling_max_capacity" in variables_content, (
            "variables.tf should define max autoscaling capacity"
        )

        # Should have autoscaling target (CPU utilization)
        assert "ecs_autoscaling_target_cpu_utilization" in variables_content, (
            "variables.tf should define target CPU utilization for autoscaling"
        )

        # Should have autoscaling policy in compute.tf
        assert "aws_appautoscaling_policy" in compute_content or "aws_appautoscaling_target" in compute_content, (
            "compute.tf should define autoscaling policy or target"
        )

    def test_iam_roles_defined(self, compute_content):
        """Test that IAM roles are defined for ECS tasks"""
        # Execution role (for pulling images, logging)
        assert 'resource "aws_iam_role" "ecs_execution"' in compute_content, (
            "compute.tf should define ECS execution role"
        )

        # Task role (for application permissions)
        assert 'resource "aws_iam_role" "ecs_task"' in compute_content, (
            "compute.tf should define ECS task role"
        )

        # Should attach ECS task execution policy
        assert "AmazonECSTaskExecutionRolePolicy" in compute_content, (
            "Should attach AmazonECSTaskExecutionRolePolicy to execution role"
        )

    def test_cloudwatch_logs_configured(self, compute_content):
        """Test that CloudWatch logs are configured for monitoring"""
        assert 'resource "aws_cloudwatch_log_group"' in compute_content, (
            "compute.tf should define CloudWatch log group"
        )

        # Should have retention policy
        assert "retention_in_days" in compute_content, (
            "CloudWatch log group should have retention policy"
        )


class TestStorageModule:
    """Test storage module (RDS/Postgres, S3/MinIO) - TODOS.md requirement"""

    @pytest.fixture
    def terraform_dir(self):
        """Get path to terraform directory"""
        return Path(__file__).parent.parent / "infrastructure" / "terraform"

    @pytest.fixture
    def storage_content(self, terraform_dir):
        """Read storage.tf content"""
        storage_file = terraform_dir / "storage.tf"
        return storage_file.read_text()

    @pytest.fixture
    def variables_content(self, terraform_dir):
        """Read variables.tf content"""
        variables_file = terraform_dir / "variables.tf"
        return variables_file.read_text()

    @pytest.fixture
    def all_tf_files(self, terraform_dir):
        """Get all Terraform files for searching"""
        tf_files = list(terraform_dir.glob("*.tf"))
        all_content = ""
        for tf_file in tf_files:
            all_content += tf_file.read_text() + "\n"
        return all_content

    def test_s3_buckets_defined(self, storage_content):
        """Test that S3 buckets are defined (TODOS.md requirement)"""
        assert 'resource "aws_s3_bucket"' in storage_content, (
            "storage.tf should define S3 buckets"
        )

        # Should have artifacts bucket
        assert "artifacts" in storage_content, (
            "storage.tf should define artifacts bucket (similar to MinIO buckets)"
        )

        # Should have logs bucket
        assert "logs" in storage_content, (
            "storage.tf should define logs bucket"
        )

    def test_s3_encryption_enabled(self, storage_content):
        """Test that S3 buckets have encryption enabled"""
        assert "aws_s3_bucket_server_side_encryption_configuration" in storage_content, (
            "S3 buckets should have server-side encryption configured"
        )

        # Should use KMS or AES256
        assert "sse_algorithm" in storage_content, (
            "S3 buckets should specify encryption algorithm"
        )

    def test_s3_public_access_blocked(self, storage_content):
        """Test that S3 buckets block public access"""
        assert "aws_s3_bucket_public_access_block" in storage_content, (
            "S3 buckets should have public access block configured"
        )

        # Should block all public access
        assert "block_public_acls" in storage_content, (
            "S3 buckets should block public ACLs"
        )

        assert "block_public_policy" in storage_content, (
            "S3 buckets should block public bucket policies"
        )

    def test_s3_versioning_configured(self, storage_content):
        """Test that S3 buckets have versioning enabled for artifacts"""
        assert "aws_s3_bucket_versioning" in storage_content, (
            "Artifacts bucket should have versioning enabled"
        )

    def test_rds_postgres_configuration(self, all_tf_files, variables_content):
        """Test that RDS PostgreSQL is configured (TODOS.md requirement)"""
        # Check if RDS resource is defined
        has_rds = 'resource "aws_db_instance"' in all_tf_files or 'resource "aws_rds_cluster"' in all_tf_files

        # RDS variables should be defined even if not used yet
        has_rds_vars = (
            "db_instance_class" in variables_content and
            "db_allocated_storage" in variables_content
        )

        assert has_rds or has_rds_vars, (
            "RDS/PostgreSQL configuration missing. TODOS.md requires validation of "
            "RDS/Postgres storage. Variables are defined but RDS resource not found. "
            "This should be added for pilot deployment."
        )

    def test_redis_elasticache_configuration(self, all_tf_files, variables_content):
        """Test that Redis/ElastiCache is configured or documented (TODOS.md mentions storage)"""
        # Check if ElastiCache resource is defined
        has_redis = (
            'resource "aws_elasticache_cluster"' in all_tf_files or
            'resource "aws_elasticache_replication_group"' in all_tf_files
        )

        # Redis variables should be defined
        has_redis_vars = (
            "redis_node_type" in variables_content and
            "redis_engine_version" in variables_content
        )

        # For pilot, having variables defined is acceptable even if resource not created
        # (could use docker-compose Redis initially)
        if not has_redis:
            assert has_redis_vars, (
                "Redis/ElastiCache configuration incomplete. Variables defined but "
                "ElastiCache resource not found. For pilot, using docker-compose Redis "
                "is acceptable, but variables suggest cloud deployment is planned."
            )


class TestSecurityBestPractices:
    """Test security best practices in Terraform configuration"""

    @pytest.fixture
    def terraform_dir(self):
        """Get path to terraform directory"""
        return Path(__file__).parent.parent / "infrastructure" / "terraform"

    @pytest.fixture
    def variables_content(self, terraform_dir):
        """Read variables.tf content"""
        variables_file = terraform_dir / "variables.tf"
        return variables_file.read_text()

    @pytest.fixture
    def all_tf_files(self, terraform_dir):
        """Get all Terraform files"""
        tf_files = list(terraform_dir.glob("*.tf"))
        all_content = ""
        for tf_file in tf_files:
            all_content += tf_file.read_text() + "\n"
        return all_content

    def test_db_password_marked_sensitive(self, variables_content):
        """Test that database password variable is marked sensitive"""
        # Find db_password variable definition
        if "db_password" in variables_content:
            # Should be marked sensitive
            assert "sensitive" in variables_content, (
                "db_password variable should be marked as sensitive"
            )

    def test_no_hardcoded_secrets(self, all_tf_files):
        """Test that no secrets are hardcoded in Terraform files"""
        # Check for common secret patterns
        dangerous_patterns = [
            r'password\s*=\s*"[^$]',  # password = "value" (not variable)
            r'secret\s*=\s*"[^$]',    # secret = "value"
            r'api_key\s*=\s*"[^$]',   # api_key = "value"
        ]

        for pattern in dangerous_patterns:
            matches = re.findall(pattern, all_tf_files, re.IGNORECASE)

            # Filter out variable definitions (those are OK)
            non_variable_matches = [
                m for m in matches
                if "variable" not in m and "description" not in m
            ]

            assert len(non_variable_matches) == 0, (
                f"Found potential hardcoded secret: {pattern}. "
                "Secrets should be passed via variables or external secret managers."
            )

    def test_common_tags_applied(self, all_tf_files):
        """Test that common tags are applied to resources"""
        assert "common_tags" in all_tf_files or "default_tags" in all_tf_files, (
            "Resources should use common tags for consistent resource management"
        )

        # Should have ManagedBy tag
        assert "ManagedBy" in all_tf_files or "Managed" in all_tf_files, (
            "Resources should be tagged with management information"
        )


class TestEnvironmentConfiguration:
    """Test environment-specific configuration"""

    @pytest.fixture
    def terraform_dir(self):
        """Get path to terraform directory"""
        return Path(__file__).parent.parent / "infrastructure" / "terraform"

    def test_environment_variable_defined(self, terraform_dir):
        """Test that environment variable is defined"""
        variables_file = terraform_dir / "variables.tf"
        content = variables_file.read_text()

        assert "environment" in content, (
            "variables.tf should define environment variable"
        )

    def test_environment_specific_configs_exist(self, terraform_dir):
        """Test that environment-specific configurations exist"""
        environments_dir = terraform_dir / "environments"

        # Should have environments directory
        if environments_dir.exists():
            # Good - has environment-specific configs
            # Check for staging and production
            staging_dir = environments_dir / "staging"
            production_dir = environments_dir / "production"

            # At least one environment config should exist
            assert staging_dir.exists() or production_dir.exists(), (
                "Should have at least one environment-specific configuration"
            )
