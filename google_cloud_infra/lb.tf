/*
resource "google_compute_health_check" "http_health_check" {
  project = var.project_id
  name    = "http-basic-health-check"
  http_health_check {
    port = 80
  }
}

resource "google_compute_backend_service" "http_backend" {
  project             = var.project_id
  name                = "llm-app-backend-service"
  protocol            = "HTTP"
  port_name           = "http"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  health_checks       = [google_compute_health_check.http_health_check.id]

  backend {
    group = google_compute_instance_group_manager.llm_app_mig.instance_group
  }

  iap {
    oauth2_client_id     = "<YOUR_OAUTH_CLIENT_ID>" # IAP設定後に取得したクライアントIDを設定
    oauth2_client_secret = "<YOUR_OAUTH_CLIENT_SECRET>" # IAP設定後に取得したクライアントシークレットを設定
  }
}

resource "google_compute_url_map" "default" {
  project         = var.project_id
  name            = "llm-app-url-map"
  default_service = google_compute_backend_service.http_backend.id
}

resource "google_compute_target_http_proxy" "default" {
  project = var.project_id
  name    = "llm-app-http-proxy"
  url_map = google_compute_url_map.default.id
}

resource "google_compute_global_forwarding_rule" "default" {
  project               = var.project_id
  name                  = "llm-app-forwarding-rule"
  target                = google_compute_target_http_proxy.default.id
  port_range            = "80"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}
*/