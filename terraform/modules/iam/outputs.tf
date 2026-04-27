output "github_service_account_email" {
  value = google_service_account.github.email
}

output "github_service_account_name" {
  value = google_service_account.github.name
}

output "jenkins_service_account_email" {
  value = google_service_account.jenkins.email
}
