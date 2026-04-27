resource "google_artifact_registry_repository" "docker" {
  project       = var.project_id
  location      = var.location
  repository_id = var.repository_id
  description   = "Docker images for CI/CD image rebuild testing"
  format        = "DOCKER"
}
