variable "project_id" {
  description = "The GCP project ID to deploy resources into."
  type        = string
  default     = "trading-daichi-ozaki213"
}

variable "region" {
  description = "The GCP region for the resources."
  type        = string
  default     = "asia-northeast1"
}

variable "zone" {
  description = "The GCP zone for the GCE instance."
  type        = string
  default     = "asia-northeast1-a"
}
