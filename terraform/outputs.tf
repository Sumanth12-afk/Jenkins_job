output "artifact_registry_repository" {
  value       = module.artifact_registry.repository_name
  description = "Artifact Registry repository resource name."
}

output "gcp_service_account" {
  value       = module.iam.github_service_account_email
  description = "GitHub Actions service account email. Store as GCP_SERVICE_ACCOUNT."
}

output "gcp_workload_identity_provider" {
  value       = module.github_oidc.provider_name
  description = "Workload Identity Provider resource name. Store as GCP_WORKLOAD_IDENTITY_PROVIDER."
}

output "jenkins_url" {
  value       = module.jenkins_vm.jenkins_url
  description = "Jenkins URL. Store as JENKINS_URL after setup."
}

output "jenkins_ssh_command" {
  value       = module.jenkins_vm.ssh_command
  description = "Command to SSH into the Jenkins VM."
}

output "docker_registry_host" {
  value       = "${var.region}-docker.pkg.dev"
  description = "Docker registry host used by Artifact Registry."
}
