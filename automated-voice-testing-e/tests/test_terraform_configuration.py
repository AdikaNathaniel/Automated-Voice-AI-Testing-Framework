"""
Tests for Terraform infrastructure configuration.

These tests validate the presence and core configuration
of Terraform files for AWS infrastructure.
"""

from pathlib import Path
import re
import pytest


@pytest.fixture(scope="module")
def terraform_dir():
    """
    Base directory for Terraform configuration files.
    """
    return Path(__file__).resolve().parent.parent / "infrastructure" / "terraform"


class TestTerraformBaseConfiguration:
    """
    Validate foundational Terraform files and provider configuration.
    """

    def test_core_files_exist(self, terraform_dir):
        required_files = {
            "main.tf",
            "providers.tf",
            "variables.tf",
            "outputs.tf",
            "locals.tf",
        }

        missing = [name for name in required_files if not (terraform_dir / name).exists()]
        assert not missing, f"Terraform base files missing: {missing}"

    def test_providers_tf_contains_terraform_and_aws_provider(self, terraform_dir):
        providers_path = terraform_dir / "providers.tf"
        assert providers_path.exists(), "providers.tf must exist"

        content = providers_path.read_text()

        assert "terraform" in content, "providers.tf should define terraform block"
        assert "required_version" in content, "terraform block should set required_version"
        assert "required_providers" in content, "terraform block should declare required providers"

        aws_provider_pattern = re.compile(r'provider\s+"aws"\s*{[^}]*region\s*=\s*var\.aws_region', re.DOTALL)
        assert aws_provider_pattern.search(content), "aws provider should reference var.aws_region"

    def test_variables_tf_defines_core_variables(self, terraform_dir):
        variables_path = terraform_dir / "variables.tf"
        assert variables_path.exists(), "variables.tf must exist"

        content = variables_path.read_text()

        required_variables = [
            "aws_region",
            "project",
            "environment",
        ]

        missing = [var for var in required_variables if f'variable "{var}"' not in content]
        assert not missing, f"Core variables missing from variables.tf: {missing}"


class TestTerraformNetworkingConfiguration:
    """
    Validate networking resources such as VPC, subnets, and security groups.
    """

    def test_variables_include_networking_inputs(self, terraform_dir):
        variables_path = terraform_dir / "variables.tf"
        assert variables_path.exists(), "variables.tf must exist for networking test"

        content = variables_path.read_text()

        required_variables = [
            "vpc_cidr",
            "public_subnet_cidrs",
            "private_subnet_cidrs",
            "availability_zones",
        ]

        missing = [var for var in required_variables if f'variable "{var}"' not in content]
        assert not missing, f"Networking variables missing: {missing}"

    def test_networking_file_exists(self, terraform_dir):
        networking_path = terraform_dir / "networking.tf"
        assert networking_path.exists(), "networking.tf must exist"

    def test_vpc_configuration(self, terraform_dir):
        networking_path = terraform_dir / "networking.tf"
        content = networking_path.read_text()

        assert 'resource "aws_vpc"' in content, "VPC resource must be defined"
        assert re.search(r"cidr_block\s*=\s*var\.vpc_cidr", content), "VPC should use vpc_cidr variable"
        assert "enable_dns_hostnames = true" in content, "VPC should enable DNS hostnames"
        assert re.search(r"tags\s*=\s*merge\(\s*local\.common_tags", content), "VPC should apply common tags"

    def test_subnet_configuration(self, terraform_dir):
        networking_path = terraform_dir / "networking.tf"
        content = networking_path.read_text()

        assert 'resource "aws_subnet" "public"' in content, "Public subnets must be defined"
        assert 'for_each = var.public_subnet_cidrs' in content, "Public subnets should iterate over provided CIDRs"
        assert 'resource "aws_subnet" "private"' in content, "Private subnets must be defined"
        assert 'for_each = var.private_subnet_cidrs' in content, "Private subnets should iterate over provided CIDRs"

    def test_security_groups_defined(self, terraform_dir):
        networking_path = terraform_dir / "networking.tf"
        content = networking_path.read_text()

        assert 'resource "aws_security_group" "app"' in content, "Application security group must be defined"
        assert 'resource "aws_security_group" "alb"' in content, "ALB security group must be defined"


class TestTerraformDataLayerConfiguration:
    """
    Validate data-layer resources including PostgreSQL and Redis.
    """

    def test_variables_include_data_inputs(self, terraform_dir):
        variables_path = terraform_dir / "variables.tf"
        content = variables_path.read_text()

        required_variables = [
            "db_name",
            "db_username",
            "db_password",
            "db_instance_class",
            "db_allocated_storage",
            "db_backup_retention_period",
            "db_multi_az",
            "redis_node_type",
            "redis_engine_version",
            "redis_port",
        ]

        missing = [var for var in required_variables if f'variable "{var}"' not in content]
        assert not missing, f"Data layer variables missing: {missing}"

    def test_data_file_exists(self, terraform_dir):
        data_path = terraform_dir / "data.tf"
        assert data_path.exists(), "data.tf must exist for data layer resources"

    def test_rds_instance_configuration(self, terraform_dir):
        content = (terraform_dir / "data.tf").read_text()

        assert 'resource "aws_db_subnet_group"' in content, "RDS subnet group must be defined"
        assert 'resource "aws_db_instance"' in content, "RDS instance must be defined"
        assert re.search(r'engine\s*=\s*"postgres"', content), "RDS engine should be postgres"
        assert re.search(r'username\s*=\s*var\.db_username', content), "RDS should reference db_username variable"
        assert re.search(r'vpc_security_group_ids\s*=\s*\[aws_security_group\.db\.id\]', content), "RDS should attach db security group"

    def test_redis_configuration(self, terraform_dir):
        content = (terraform_dir / "data.tf").read_text()

        assert 'resource "aws_elasticache_subnet_group"' in content, "ElastiCache subnet group must be defined"
        assert 'resource "aws_elasticache_replication_group"' in content, "Redis replication group must be defined"
        assert re.search(r'engine\s*=\s*"redis"', content), "Redis engine should be redis"
        assert re.search(r'security_group_ids\s*=\s*\[aws_security_group\.redis\.id\]', content), "Redis should attach redis security group"


class TestTerraformStorageConfiguration:
    """
    Validate S3 bucket resources for artifacts and logs.
    """

    def test_variables_include_storage_inputs(self, terraform_dir):
        content = (terraform_dir / "variables.tf").read_text()

        required_variables = [
            "artifact_bucket_force_destroy",
            "log_bucket_expiration_days",
        ]

        missing = [var for var in required_variables if f'variable "{var}"' not in content]
        assert not missing, f"Storage variables missing: {missing}"

    def test_storage_file_exists(self, terraform_dir):
        storage_path = terraform_dir / "storage.tf"
        assert storage_path.exists(), "storage.tf must exist for S3 resources"

    def test_artifact_bucket_configuration(self, terraform_dir):
        content = (terraform_dir / "storage.tf").read_text()

        assert 'resource "aws_s3_bucket" "artifacts"' in content, "Artifacts bucket must be defined"
        assert re.search(r'bucket\s*=\s*"\${local\.name_prefix}-artifacts"', content), "Artifacts bucket should use standardized name"
        assert 'resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts"' in content, "Artifacts bucket should enforce encryption via dedicated resource"
        assert 'resource "aws_s3_bucket_versioning" "artifacts"' in content, "Artifacts bucket should configure versioning via dedicated resource"

    def test_log_bucket_configuration(self, terraform_dir):
        content = (terraform_dir / "storage.tf").read_text()

        assert 'resource "aws_s3_bucket" "logs"' in content, "Logs bucket must be defined"
        assert re.search(r'bucket\s*=\s*"\${local\.name_prefix}-logs"', content), "Logs bucket should use standardized name"
        assert "lifecycle_rule" in content, "Logs bucket should define lifecycle rules"
        assert 'resource "aws_s3_bucket_server_side_encryption_configuration" "logs"' in content, "Logs bucket should enforce encryption via dedicated resource"


class TestTerraformComputeConfiguration:
    """
    Validate ECS Fargate and Application Load Balancer resources.
    """

    def test_variables_include_compute_inputs(self, terraform_dir):
        content = (terraform_dir / "variables.tf").read_text()

        required_variables = [
            "ecs_cluster_name",
            "ecs_task_cpu",
            "ecs_task_memory",
            "container_port",
            "desired_task_count",
            "app_image",
            "alb_internal",
            "enable_ecs_autoscaling",
            "ecs_autoscaling_min_capacity",
            "ecs_autoscaling_max_capacity",
            "ecs_autoscaling_target_cpu_utilization",
        ]

        missing = [var for var in required_variables if f'variable "{var}"' not in content]
        assert not missing, f"Compute variables missing: {missing}"

    def test_compute_file_exists(self, terraform_dir):
        compute_path = terraform_dir / "compute.tf"
        assert compute_path.exists(), "compute.tf must exist for ECS resources"

    def test_ecs_cluster_and_task_definition(self, terraform_dir):
        content = (terraform_dir / "compute.tf").read_text()

        assert 'resource "aws_ecs_cluster"' in content, "ECS cluster must be defined"
        assert 'resource "aws_ecs_task_definition"' in content, "ECS task definition must be defined"
        assert re.search(r'requires_compatibilities\s*=\s*\[\s*"FARGATE"\s*\]', content), "Task definition must target Fargate"
        assert re.search(r'cpu\s*=\s*var\.ecs_task_cpu', content), "Task definition should use ecs_task_cpu variable"
        assert re.search(r'memory\s*=\s*var\.ecs_task_memory', content), "Task definition should use ecs_task_memory variable"

    def test_ecs_service_and_load_balancer(self, terraform_dir):
        content = (terraform_dir / "compute.tf").read_text()

        assert 'resource "aws_ecs_service"' in content, "ECS service must be defined"
        assert re.search(r'desired_count\s*=\s*var\.desired_task_count', content), "Service should use desired_task_count variable"
        assert re.search(r'load_balancer\s*{', content), "Service should configure load balancer block"
        assert re.search(r'tg\.arn', content), "Service should attach to target group"

    def test_load_balancer_resources(self, terraform_dir):
        content = (terraform_dir / "compute.tf").read_text()

        assert 'resource "aws_lb"' in content, "Application Load Balancer must be defined"
        assert 'resource "aws_lb_target_group"' in content, "Target group must be defined"
        assert 'resource "aws_lb_listener"' in content, "Listener must be defined"

    def test_autoscaling_resources_defined(self, terraform_dir):
        content = (terraform_dir / "compute.tf").read_text()

        assert 'resource "aws_appautoscaling_target"' in content, "ECS service should register an autoscaling target"
        assert re.search(r'min_capacity\s*=\s*var\.ecs_autoscaling_min_capacity', content), (
            "Autoscaling target should use ecs_autoscaling_min_capacity variable"
        )
        assert re.search(r'max_capacity\s*=\s*var\.ecs_autoscaling_max_capacity', content), (
            "Autoscaling target should use ecs_autoscaling_max_capacity variable"
        )
        assert 'resource "aws_appautoscaling_policy"' in content, "ECS service should define autoscaling policy"
        assert re.search(r'target_tracking_scaling_policy_configuration', content), (
            "Autoscaling policy should be target tracking"
        )
        assert re.search(r'target_value\s*=\s*var\.ecs_autoscaling_target_cpu_utilization', content), (
            "Autoscaling policy should target CPU utilization variable"
        )
