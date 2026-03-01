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

# Service Account para GKE
resource "google_service_account" "gke_sa" {
  account_id   = "cactus-gke-sa"
  display_name = "Service Account para GKE"
}

# Cluster GKE
resource "google_container_cluster" "cactus_cluster" {
  name     = "cactus-cluster"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  service_account = google_service_account.gke_sa.email

  addons_config {
    http_load_balancing {
      disabled = true
    }
    network_policy_config {
      disabled = true
    }
  }
}

# Node Pool para GKE
resource "google_container_node_pool" "cactus_nodes" {
  name       = "cactus-node-pool"
  location   = var.region
  cluster    = google_container_cluster.cactus_cluster.name
  node_count = 1

  node_config {
    machine_type = "e2-medium"
    service_account = google_service_account.gke_sa.email
    
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
