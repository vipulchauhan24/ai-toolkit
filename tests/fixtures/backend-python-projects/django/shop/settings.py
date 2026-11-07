import os

DEBUG = os.environ.get("DEBUG", "") == "1"
SECRET_KEY = os.environ["SECRET_KEY"]
INSTALLED_APPS = ["django.contrib.contenttypes", "orders"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}}
