output "db_instance_ip" {
  value = google_sql_database_instance.cactus_db.public_ip_address
}

output "db_instance_name" {
  value = google_sql_database_instance.cactus_db.name
}

output "db_connection_string" {
  value = "postgresql://${google_sql_user.cactus_user.name}:${var.db_password}@${google_sql_database_instance.cactus_db.public_ip_address}/${google_sql_database.cactus.name}"
  sensitive = true
}
