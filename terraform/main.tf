terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.61.0"
    }
  }
}

provider "google" {

  credentials = file("credentials.json")

  project = var.google_project_id
  region  = var.region
  zone    = var.region
}

resource "google_storage_bucket" "bucket" {
  name = "budget-handler-storage"
}


data "archive_file" "code" {
  type        = "zip"
  output_path = var.output_code
  source_dir  = var.source_code
}

resource "google_storage_bucket_object" "archive" {
  name       = "index.zip"
  bucket     = google_storage_bucket.bucket.name
  source     = var.output_code
  depends_on = [data.archive_file.code]
}

resource "google_cloudfunctions_function" "function" {
  name        = "budget-handler"
  description = "automated budget handler"
  runtime     = "python38"

  max_instances         = 1
  available_memory_mb   = 128
  timeout               = 60
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = var.pubsub_topic
  }
  environment_variables = {
    "GCP_PROJECT" = var.google_project_id
  }
  entry_point           = "main"
  service_account_email = var.service_account
  depends_on = [
    google_storage_bucket_object.archive
  ]
}

/*
# IAM entry for service account to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:" + var.service_account
}*/
