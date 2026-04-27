variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  description = "Bucket location."
  default     = "us-central1"
}

variable "bucket_name" {
  type        = string
  description = "Globally unique GCS bucket name for Terraform state."
}
