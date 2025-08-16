resource "google_service_account" "gce_service_account" {
  project      = var.project_id
  account_id   = "gce-llm-app-sa"
  display_name = "Service Account for LLM App GCE Instances"
}

# GCEからGCS, Pub/Sub, Cloud SQLにアクセスするための権限を付与
resource "google_project_iam_member" "storage_reader" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.gce_service_account.email}"
}

resource "google_project_iam_member" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.gce_service_account.email}"
}

resource "google_project_iam_member" "pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.gce_service_account.email}"
}

resource "google_project_iam_member" "sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.gce_service_account.email}"
}
