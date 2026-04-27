resource "google_service_account" "github" {
  project      = var.project_id
  account_id   = var.github_service_account
  display_name = "Image rebuild GitHub Actions"
}

resource "google_service_account" "jenkins" {
  project      = var.project_id
  account_id   = var.jenkins_service_account
  display_name = "Image rebuild Jenkins VM"
}

locals {
  github_roles = [
    "roles/artifactregistry.reader",
    "roles/datastore.user",
  ]

  jenkins_roles = [
    "roles/artifactregistry.reader",
    "roles/artifactregistry.writer",
  ]
}

resource "google_project_iam_member" "github_roles" {
  for_each = toset(local.github_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.github.email}"
}

resource "google_project_iam_member" "jenkins_roles" {
  for_each = toset(local.jenkins_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.jenkins.email}"
}
