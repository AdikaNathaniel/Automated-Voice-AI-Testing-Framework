############################################################
# Root module for the Voice AI Testing Platform infrastructure
# Additional resource definitions are split across *.tf files
# within this directory for clarity.
############################################################

data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}
