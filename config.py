import os

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "2385",
    "database": "garment_automation"
}
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")