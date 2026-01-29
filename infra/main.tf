terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_sql_database_instance" "cactus_db" {
  name             = "cactus-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
  }

  deletion_protection = false # Para poder borrar fácilmente en desarrollo
}

resource "google_sql_database" "cactus" {
  name     = "cactus"
  instance = google_sql_database_instance.cactus_db.name
}

resource "google_sql_user" "cactus_user" {
  name     = "cactus_user"
  instance = google_sql_database_instance.cactus_db.name
  password = var.db_password
}
