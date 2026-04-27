variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "services" {
  type        = list(string)
  description = "GCP APIs to enable."
  default = [
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "compute.googleapis.com",
    "firestore.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com",
  ]
}
