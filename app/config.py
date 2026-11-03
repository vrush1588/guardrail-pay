import os

from dotenv import load_dotenv

load_dotenv()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET", "")
PAYPAL_BASE = os.getenv("PAYPAL_BASE", "https://api-m.sandbox.paypal.com")
# "mock" (default) fakes every PayPal call; "sandbox" makes real calls to PAYPAL_BASE.
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "mock").strip().lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

BASE_URL = os.getenv("GUARDRAIL_BASE_URL", "http://127.0.0.1:8000")
