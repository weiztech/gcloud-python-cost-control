variable "google_project_id" {
  description = "Google project name"
  type        = string
}


variable "region" {
  description = "Google region name"
  type        = string
}

variable "pubsub_topic" {
  description = "Google region name"
  type        = string
}

variable "service_account" {
  description = "Google service account"
  type        = string
}

variable "source_code" {
  type = string
}

variable "output_code" {
  type = string
}

output "source_code" {
  value = var.source_code
}

output "output_code" {
  value = var.output_code
}
