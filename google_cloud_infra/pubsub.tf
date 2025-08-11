resource "google_pubsub_topic" "doc_update_topic" {
  project = var.project_id
  name    = "document-update-topic"
}

resource "google_pubsub_subscription" "doc_update_sub" {
  project = var.project_id
  name    = "document-update-subscription"
  topic   = google_pubsub_topic.doc_update_topic.name

  ack_deadline_seconds = 60
}
