output "network_self_link" {
  value = google_compute_network.main.self_link
}

output "subnet_self_link" {
  value = google_compute_subnetwork.main.self_link
}
