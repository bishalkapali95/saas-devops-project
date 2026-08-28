# ==============================================================================
# Terraform Configuration: SaaS Password-Reset Infrastructure as Code (IaC)
# ==============================================================================
# DevOps Concept - Infrastructure as Code (IaC):
# IaC allows teams to define and manage infrastructure (servers, networks, configs)
# using declarative code files rather than manual point-and-click console clicks.
#
# Key Benefits demonstrated here:
# 1. Reproducibility: Dev, Staging, and Production share identical topology.
# 2. Drift Reduction: Terraform compares the desired state (code) against actual
#    state (`terraform.tfstate`) and calculates the exact delta.
# 3. Version Control & Auditability: Infrastructure changes go through Git PRs.
# 4. Zero Cloud Cost: Uses the `local` provider for safe, self-contained demonstration.
# ==============================================================================

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5.0"
    }
  }
}

# ------------------------------------------------------------------------------
# Input Variables
# ------------------------------------------------------------------------------
variable "environment" {
  type        = string
  description = "Target deployment environment (dev, staging, or production)"
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "The environment variable must be one of: dev, staging, production."
  }
}

variable "app_port" {
  type        = number
  description = "Network port exposed by the container service"
  default     = 5000
}

variable "enable_ssl" {
  type        = bool
  description = "Whether SSL/TLS termination is enforced in this environment"
  default     = false
}

# ------------------------------------------------------------------------------
# Local Variables / Computed Environment Logic
# ------------------------------------------------------------------------------
locals {
  app_name = "saas-password-reset"
  
  # Environment-specific parameter tuning
  # In a cloud setup, production might have higher replicas or stricter SSL
  replica_count = var.environment == "production" ? 3 : (var.environment == "staging" ? 2 : 1)
  
  # Safe placeholder secrets (demonstrates configuration without storing real secrets)
  database_url_placeholder  = "postgresql://user:***@db.${var.environment}.internal:5432/${local.app_name}"
  email_api_key_placeholder = "placeholder_key_${var.environment}_only"
}

# ------------------------------------------------------------------------------
# Resource: Local Deployment Manifest / Configuration File
# ------------------------------------------------------------------------------
# In a full cloud setup, this would be `aws_ecs_service`, `azurerm_container_group`,
# or `google_cloud_run_service`. For this Level 5 assessment, we manage a local JSON
# deployment manifest to demonstrate state tracking and variable interpolation safely.
resource "local_file" "environment_manifest" {
  filename = "${path.module}/generated_${var.environment}_manifest.json"
  content = jsonencode({
    application      = local.app_name
    environment      = var.environment
    replica_count    = local.replica_count
    port             = var.app_port
    ssl_enforced     = var.environment == "production" ? true : var.enable_ssl
    health_endpoint  = "/health"
    database_url_ref = local.database_url_placeholder
    email_service    = "Transactional-Mock-${var.environment}"
    managed_by       = "Terraform-IaC"
  })
}

# ------------------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------------------
output "deployment_summary" {
  description = "Summary of deployed infrastructure parameters"
  value = {
    application      = local.app_name
    target_env       = var.environment
    replicas         = local.replica_count
    manifest_path    = local_file.environment_manifest.filename
    health_check_url = "http://localhost:${var.app_port}/health"
  }
}
