resource "google_compute_network" "vpc_network" {
  project                 = var.project_id
  name                    = "gce-vpc-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "gce_subnet" {
  project                  = var.project_id
  name                     = "gce-subnet"
  ip_cidr_range            = "10.0.1.0/24"
  region                   = var.region
  network                  = google_compute_network.vpc_network.id
  private_ip_google_access = true
}

# IAPからのSSH接続を許可
resource "google_compute_firewall" "allow_iap_ssh" {
  project = var.project_id
  name    = "allow-iap-ssh-ingress"
  network = google_compute_network.vpc_network.name
  direction = "INGRESS"
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = ["35.235.240.0/20"] # IAP for TCP forwardingのIP範囲
  target_tags = ["allow-ssh"]
}

# LBからのヘルスチェックを許可
resource "google_compute_firewall" "allow_health_check" {
  project = var.project_id
  name    = "allow-lb-health-check"
  network = google_compute_network.vpc_network.name
  direction = "INGRESS"
  allow {
    protocol = "tcp"
    ports    = ["80"] # アプリケーションのポートに合わせてください
  }
  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]
  target_tags = ["http-server"]
}

# LBからインスタンスへのHTTPトラフィックを許可
resource "google_compute_firewall" "allow_http_from_lb" {
  project = var.project_id
  name    = "allow-http-from-lb"
  network = google_compute_network.vpc_network.name
  direction = "INGRESS"
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
  source_tags = ["http-server"] # LB自体にはタグが付かないため、MIGのインスタンスにタグを付ける
  target_tags = ["http-server"]
}