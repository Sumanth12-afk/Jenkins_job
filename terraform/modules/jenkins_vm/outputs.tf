output "external_ip" {
  value = google_compute_instance.jenkins.network_interface[0].access_config[0].nat_ip
}

output "jenkins_url" {
  value = "http://${google_compute_instance.jenkins.network_interface[0].access_config[0].nat_ip}:8080"
}

output "ssh_command" {
  value = "gcloud compute ssh ${google_compute_instance.jenkins.name} --zone ${var.zone} --project ${var.project_id}"
}
