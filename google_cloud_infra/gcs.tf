resource "google_storage_bucket" "app_bucket" {
  project      = var.project_id
  name         = "app-data-bucket-${var.project_id}" # 一意なバケット名
  location     = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}
