import os

import boto3
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from google.cloud import secretmanager


def get_secret(name: str, default: str | None = None) -> str | None:
    backend = os.getenv("SECRET_BACKEND", "env").lower()

    # 1. Docker/K8s file secrets
    secret_file = f"/run/secrets/{name}"
    if os.path.isfile(secret_file):
        with open(secret_file) as f:
            return f.read().strip()

    # 2. Environment variable
    if backend == "env":
        return os.getenv(name, default)

    # 3. Cloud backends
    if backend == "aws" and boto3:
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=name)
        return resp.get("SecretString")

    if backend == "gcp" and secretmanager:
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv("GCP_PROJECT_ID")
        secret_path = f"projects/{project_id}/secrets/{name}/versions/latest"
        resp = client.access_secret_version(name=secret_path)
        return resp.payload.data.decode("UTF-8")

    if backend == "azure" and SecretClient and DefaultAzureCredential:
        keyvault_url = os.getenv("AZURE_KEYVAULT_URL")
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=keyvault_url, credential=credential)
        secret = client.get_secret(name)
        return secret.value

    return default

current_script_path = os.path.dirname(os.path.abspath(__file__))
Base_directory = current_script_path + os.path.sep
glassdoor_jobs_output_directory = f"{Base_directory}../glassdoor-scrap-jobs-data/"
GLASSDOOR_JOBS_FILE = f"{glassdoor_jobs_output_directory}job_listings_glassdoor.json"

REQUIRED_KEYWORDS = ["data & analytics", "bi developer", "insight analyst", "data scientist", "insights analyst", "technical project manager", "business intelligence", "bi analyst", "data engineer", "bi engineer", "data analyst"]
EXCLUDED_KEYWORDS = ["stage", "intern"]
LOCATION_TYPE_MAPPING = {"IS": "STATE", "IC": "CITY", "IN": "COUNTRY"}
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAMBOTTOKEN")
TELEGRAM_BOT_CHAT_ID = os.getenv("TELEGRAMBOTCHATID")
API_TOKEN = os.getenv("API_TOKEN")
JOBS_LOOKBACK = 6
JOBS_PRUNING = 10

JOB_TO_SEARCH=[{"keyword":"Data analyst", "location": "Toulouse"},
               {"keyword":"Data engineer", "location": "Toulouse"},
               {"keyword":"Power BI", "location": "Toulouse"}]

# --- Selenium Options (Minimal set) ---
CHROME_OPTIONS = [
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "start-maximized",
    "disable-infobars",
    "--disable-extensions",
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
]

NOTIFICATION_CHANNELS = {
    "telegram": {
        "enabled": True,
        "token": TELEGRAM_BOT_TOKEN,
        "chat_id": TELEGRAM_BOT_CHAT_ID,
    }
}
