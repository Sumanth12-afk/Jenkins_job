resource "google_compute_network" "main" {
  project                 = var.project_id
  name                    = var.network_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "main" {
  project       = var.project_id
  name          = var.subnet_name
  region        = var.region
  ip_cidr_range = var.subnet_cidr
  network       = google_compute_network.main.id
}

resource "google_compute_firewall" "jenkins_ui" {
  project = var.project_id
  name    = "${var.network_name}-allow-jenkins-ui"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = var.jenkins_allowed_source_ranges
  target_tags   = ["jenkins"]
}

resource "google_compute_firewall" "ssh" {
  project = var.project_id
  name    = "${var.network_name}-allow-ssh"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = var.jenkins_allowed_source_ranges
  target_tags   = ["jenkins"]
}
