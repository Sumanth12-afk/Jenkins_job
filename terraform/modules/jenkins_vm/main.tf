resource "google_compute_instance" "jenkins" {
  project      = var.project_id
  name         = var.vm_name
  zone         = var.zone
  machine_type = var.machine_type
  tags         = ["jenkins"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 40
      type  = "pd-balanced"
    }
  }

  network_interface {
    network    = var.network_self_link
    subnetwork = var.subnet_self_link

    access_config {}
  }

  service_account {
    email  = var.service_account_email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  metadata_startup_script = templatefile("${path.module}/startup.sh.tftpl", {
    region                 = var.region
    project_id             = var.project_id
    artifact_registry_repo = var.artifact_registry_repo
  })

  allow_stopping_for_update = true
}
