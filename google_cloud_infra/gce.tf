resource "google_compute_instance_template" "llm_app_template" {
  project      = var.project_id
  name_prefix  = "llm-app-template-"
  machine_type = "g2-standard-4" # GPUタイプは適宜変更してください
  region       = var.region

  scheduling {
    provisioning_model = "SPOT" # Spot VMを利用
    instance_termination_action = "DELETE"
  }

  disk {
    source_image = "debian-cloud/debian-11"
    auto_delete  = true
    boot         = true
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.gce_subnet.id
  }

  service_account {
    email  = google_service_account.gce_service_account.email
    scopes = ["cloud-platform"]
  }

  tags = ["http-server", "allow-ssh"]

  // 起動スクリプトなどでアプリケーションのセットアップを想定
  metadata_startup_script = <<-EOT
    #!/bin/bash
    echo "Setting up server..."
    # apt-get update, install docker, etc.
  EOT
}

resource "google_compute_instance_group_manager" "llm_app_mig" {
  project            = var.project_id
  zone               = var.zone
  name               = "llm-app-mig"
  base_instance_name = "llm-app-vm"

  version {
    instance_template = google_compute_instance_template.llm_app_template.id
  }

  target_size = 1 # 初期インスタンス数

  named_port {
    name = "http"
    port = 80
  }
}