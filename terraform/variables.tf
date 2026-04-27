variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "project_number" {
  description = "Numeric GCP project number used in Workload Identity principal strings."
  type        = string
}

variable "region" {
  description = "Primary GCP region."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Primary GCP zone."
  type        = string
  default     = "us-central1-a"
}

variable "firestore_location" {
  description = "Firestore database location."
  type        = string
  default     = "nam5"
}

variable "github_repo" {
  description = "GitHub repository allowed to impersonate the GCP service account, in owner/repo format."
  type        = string
}

variable "github_oidc_pool_id" {
  description = "Workload Identity Pool ID for GitHub Actions."
  type        = string
  default     = "github-pool"
}

variable "github_oidc_provider_id" {
  description = "Workload Identity Provider ID for GitHub Actions."
  type        = string
  default     = "github-provider"
}

variable "github_service_account" {
  description = "Service account ID used by GitHub Actions."
  type        = string
  default     = "image-rebuild-github"
}

variable "jenkins_service_account" {
  description = "Service account ID attached to the Jenkins VM."
  type        = string
  default     = "image-rebuild-jenkins"
}

variable "artifact_registry_repo" {
  description = "Artifact Registry Docker repository ID."
  type        = string
  default     = "microservices"
}

variable "network_name" {
  description = "VPC network name."
  type        = string
  default     = "image-rebuild-vpc"
}

variable "subnet_name" {
  description = "Subnet name."
  type        = string
  default     = "image-rebuild-subnet"
}

variable "subnet_cidr" {
  description = "Subnet CIDR."
  type        = string
  default     = "10.42.0.0/24"
}

variable "jenkins_vm_name" {
  description = "Jenkins VM name."
  type        = string
  default     = "jenkins-rebuild-test"
}

variable "jenkins_machine_type" {
  description = "Jenkins VM machine type."
  type        = string
  default     = "e2-medium"
}

variable "jenkins_allowed_source_ranges" {
  description = "CIDR ranges allowed to access Jenkins UI and SSH. Use your public IP /32 for testing."
  type        = list(string)
}
