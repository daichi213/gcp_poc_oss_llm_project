/*
output "load_balancer_ip" {
  description = "The IP address of the external load balancer."
  value       = google_compute_global_forwarding_rule.default.ip_address
}
*/

output "gcs_bucket_name" {
  description = "Name of the GCS bucket for master documents."
  value       = google_storage_bucket.app_bucket.name
}

output "db_instance_connection_name" {
  description = "The connection name of the Cloud SQL instance to be used by Cloud SQL Proxy."
  value       = google_sql_database_instance.postgres.connection_name
}
