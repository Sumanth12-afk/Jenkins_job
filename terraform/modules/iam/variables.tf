variable "project_id" {
  type = string
}

variable "github_service_account" {
  type = string
}

variable "jenkins_service_account" {
  type = string
}

variable "artifact_registry_reader" {
  type    = bool
  default = true
}

variable "artifact_registry_writer" {
  type    = bool
  default = true
}
