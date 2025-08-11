variable "db_user" {
  description = "The username for the Cloud SQL database."
  type        = string
  default     = "app-user"
}

variable "db_password" {
  description = "The password for the Cloud SQL database user."
  type        = string
  sensitive   = true
}

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
  name     = var.db_user
  password = var.db_password
}
