import os
import dj_database_url
from pathlib import Path
import cloudinary_storage
BASE_DIR = Path(__file__).resolve().parent.parent


# -------------------------------
# SECURITY SETTINGS
# -------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

# Detect if running on Render
IS_RENDER = "RENDER_INTERNAL_HOSTNAME" in os.environ

#DEBUG = not IS_RENDER  # AUTO TURN OFF DEBUG ON RENDER
DEBUG = True

ALLOWED_HOSTS = [
    "naturesuplift.com",
    "www.naturesuplift.com",
    "natures-uplift-3.onrender.com",
    "cloudinary",
    "cloudinary_storage",
    "natures-uplift-5inz.onrender.com",
    "natures-uplift-z9bl.onrender.com",
    "shop.naturesuplift.com",
    "natures-uplift-10.onrender.com",
    "127.0.0.1",
    "localhost",
]
  # Render injects host automatically

SECURE_SSL_REDIRECT = False
# -------------------------------
# INSTALLED APPS
# -------------------------------
INSTALLED_APPS = [
    "accounts",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "cloudinary",
    "cloudinary_storage",

    "plants",
    "payments",
    "django.contrib.sites",          # Required
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
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
    "allauth.account.middleware.AccountMiddleware",
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
                "accounts.context_processors.auth_links",
                "accounts.context_processors.cart_count",
                "plants.context_processors.cart_count",
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



AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# -------------------------------
# OTHER CONFIG
# -------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

AUTH_PASSWORD_VALIDATORS = []


AUTH_USER_MODEL = 'accounts.CustomUser'


# Sites framework
SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '7034000444-v098kotj3180egdo1aomtt8r4gobfao9.apps.googleusercontent.com',
            'secret': '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',
        }
    }
}


# Optional settings for allauth
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'phone'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
LOGIN_REDIRECT_URL = '/'       # redirect after login
LOGOUT_REDIRECT_URL = '/'      # redirect after logout


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"

EMAIL_HOST_USER = os.environ.get(
    "EMAIL_HOST_USER",
    "naturesuplift.otp@gmail.com"
)

EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD",
    "nbduperlbgosefqv"
)

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "Natures Uplift <naturesuplift71@gmail.com>"
)

# MUST be a list (used by EmailMultiAlternatives)
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "naturesuplift71@gmail.com")

# Always normalize to list
if isinstance(ADMIN_EMAIL, str):
    ADMIN_EMAIL = [ADMIN_EMAIL]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

