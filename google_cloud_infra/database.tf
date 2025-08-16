resource "google_sql_database_instance" "postgres" {
  project             = var.project_id
  name                = "llm-app-db-instance"
  database_version    = "POSTGRES_15"
  region              = var.region

  settings {
    tier = "db-g1-small"
    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.vpc_network.id
    }
  }
}

resource "google_sql_database" "default" {
  project  = var.project_id
  instance = google_sql_database_instance.postgres.name
  name     = "vector-db"
}

resource "google_sql_user" "default" {
  project  = var.project_id
  instance = google_sql_database_instance.postgres.name
  name     = trimsuffix(google_service_account.gce_service_account.email, ".gserviceaccount.com")
  type     = "IAM_USER"
}
