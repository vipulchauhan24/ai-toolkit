"""Settings read from the environment."""
import os

DEBUG = os.environ.get("DEBUG", "") == "1"
SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
