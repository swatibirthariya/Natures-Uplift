import os
import dj_database_url
from pathlib import Path
import cloudinary
import cloudinary_storage
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------
# SECURITY SETTINGS
# -------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

# Detect if running on Render
IS_RENDER = "RENDER_INTERNAL_HOSTNAME" in os.environ

DEBUG = not IS_RENDER  # AUTO TURN OFF DEBUG ON RENDER

ALLOWED_HOSTS = [
    "naturesuplift.com",
    "www.naturesuplift.com",
    "natures-uplift-3.onrender.com",
    "cloudinary",
    "cloudinary_storage",
    "natures-uplift-5inz.onrender.com",
    "127.0.0.1",
    "localhost",
]
  # Render injects host automatically
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
)

SECURE_SSL_REDIRECT = False
# -------------------------------
# INSTALLED APPS
# -------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "plants",
]


# -------------------------------
# MIDDLEWARE + WHITENOISE
# -------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # IMPORTANT FOR RENDER STATIC FILES
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "natures_uplift.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "natures_uplift.wsgi.application"


# -------------------------------
# DATABASES
# -------------------------------
if IS_RENDER:
    # Production database (Render)
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # LOCAL development PostgreSQL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "nature_db",
            "USER": "nature_uplift",
            "PASSWORD": "Rounak@123",  # safe locally
            "HOST": "localhost",
            "PORT": "5432",
        }
    }


# -------------------------------
# STATIC & MEDIA FILES
# -------------------------------
STATIC_URL = "/static/"

# Location of your local static folder
STATICFILES_DIRS = [BASE_DIR / "static"]

# Location where collectstatic will place files
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise static compression & versioning
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
#MEDIA_ROOT = BASE_DIR / "media"


# -------------------------------
# OTHER CONFIG
# -------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

AUTH_PASSWORD_VALIDATORS = []
