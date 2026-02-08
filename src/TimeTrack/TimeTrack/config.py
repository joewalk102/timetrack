from os import environ

from library.gcloud.sec_mgr import SecretManagerClient

smc = SecretManagerClient(project_id=environ.get("GCP_PROJECT_ID"))
loaded_vars = smc.load_secret_to_env(environ.get("GCP_SECRET_NAME"))

secret_key = environ.get("SECRET_KEY")
allowed_hosts = environ.get("ALLOWED_HOSTS", "*").split(",")
debug = environ.get("DEBUG", "True").lower() == "true"

db_environment = environ.get("DB_ENVIRONMENT", "local").lower()
db_name = environ.get("DB_NAME")
db_user = environ.get("DB_USER")
db_pass = environ.get("DB_PASS")
db_host = environ.get("DB_HOST")
db_port = environ.get("DB_PORT")
