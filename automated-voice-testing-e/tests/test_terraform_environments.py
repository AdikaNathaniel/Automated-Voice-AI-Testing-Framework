"""
Tests for environment-specific Terraform configurations.

Validates that staging infrastructure overrides base module defaults
with environment-appropriate settings (smaller footprint and isolated data).
"""

from pathlib import Path
import re


class TestTerraformStagingEnvironment:
    """
    Validate staging-specific Terraform configuration.
    """

    @property
    def staging_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent / "infrastructure" / "terraform" / "environments" / "staging"

    def test_staging_directory_and_main_file_exist(self):
        staging_dir = self.staging_dir
        assert staging_dir.exists(), "Staging environment directory must exist"

        main_tf = staging_dir / "main.tf"
        assert main_tf.exists(), "Staging environment must define main.tf"

    def test_staging_module_uses_root_configuration(self):
        content = (self.staging_dir / "main.tf").read_text()

        assert 'module "staging"' in content, "Staging environment should declare a module named 'staging'"
        assert 'source = "../.."' in content, "Staging module must reference the root Terraform configuration"
        assert re.search(r'environment\s*=\s*"staging"', content), "Staging module must set environment = \"staging\""

    def test_staging_overrides_resource_sizes(self):
        content = (self.staging_dir / "main.tf").read_text()

        assert re.search(r'db_instance_class\s*=\s*"db\.t3\.small"', content), "Staging should use a smaller DB instance class"
        assert re.search(r'desired_task_count\s*=\s*1', content), "Staging should reduce ECS task count to 1"
        assert re.search(r'app_image\s*=\s*".*:staging"', content), "Staging should pin application image to a staging tag"

    def test_staging_uses_separate_database_identifier(self):
        content = (self.staging_dir / "main.tf").read_text()
        assert re.search(r'db_name\s*=\s*"voice_ai_testing_staging"', content), "Staging must use a distinct database name"


class TestTerraformProductionEnvironment:
    """
    Validate production-specific Terraform configuration.
    """

    @property
    def production_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent / "infrastructure" / "terraform" / "environments" / "production"

    def test_production_directory_and_main_file_exist(self):
        production_dir = self.production_dir
        assert production_dir.exists(), "Production environment directory must exist"

        main_tf = production_dir / "main.tf"
        assert main_tf.exists(), "Production environment must define main.tf"

    def test_production_module_configuration(self):
        content = (self.production_dir / "main.tf").read_text()

        assert 'module "production"' in content, "Production environment should declare a module named 'production'"
        assert 'source = "../.."' in content, "Production module must reference the root Terraform configuration"
        assert re.search(r'environment\s*=\s*"production"', content), "Production module must set environment = \"production\""

    def test_production_enables_multi_az_and_scaling(self):
        content = (self.production_dir / "main.tf").read_text()

        assert re.search(r'db_multi_az\s*=\s*true', content), "Production should enable Multi-AZ for the database"
        assert re.search(r'db_allocated_storage\s*=\s*100', content), "Production should allocate more storage for the database"
        assert re.search(r'availability_zones\s*=\s*\[.*"us-east-1a".*"us-east-1b".*"us-east-1c"', content, re.DOTALL), (
            "Production should target at least three availability zones"
        )
        assert re.search(r'desired_task_count\s*=\s*3', content), "Production should increase ECS desired task count"
        assert re.search(r'enable_ecs_autoscaling\s*=\s*true', content), "Production should enable ECS auto scaling"
        assert re.search(r'ecs_autoscaling_min_capacity\s*=\s*3', content), "Production should set autoscaling min capacity"
        assert re.search(r'ecs_autoscaling_max_capacity\s*=\s*10', content), "Production should set autoscaling max capacity"

    def test_production_uses_distinct_identifiers(self):
        content = (self.production_dir / "main.tf").read_text()

        assert re.search(r'db_name\s*=\s*"voice_ai_testing_prod"', content), "Production must use a distinct database name"
        assert re.search(r'app_image\s*=\s*".*:production"', content), "Production should deploy a production-tagged image"
