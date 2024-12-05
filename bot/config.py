from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

_main_bot_token = os.getenv("ALLES_HELPER_BOT_TOKEN")
_test_bot_token = os.getenv("DEBUG_ALLES_BOT_TOKEN")
auth_api_token = os.getenv("AUTH_API_TOKEN")
server_ip = "http://79.174.84.241"

database_connection = {
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "database": "helper",
    "host": "helper_bot_psg",
    "port": "5432"
}

tg_token = _test_bot_token
