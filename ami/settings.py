import os
import sys
from pathlib import Path

import dj_database_url
import sentry_sdk
from dotenv import dotenv_values

import vapid_keys

CONFIG = {
    **dotenv_values(".env"),
    **dotenv_values(".env.local"),
    **dotenv_values(".env.development"),
    **dotenv_values(".env.development.local"),
    **os.environ,  # override loaded values with environment variables
}

# Generate VAPID keys for Webpush if absent
CONFIG = vapid_keys.initialize(CONFIG)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG["DJANGO_SECRET_KEY"]
assert SECRET_KEY, "set a random DJANGO_SECRET_KEY in your .env.local file"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIG["DEBUG"] == "true"

ALLOWED_HOSTS = [
    ".osc-fr1.scalingo.io",
    "ami-back-prod.osc-secnum-fr1.scalingo.io",
]


# Application definition

INSTALLED_APPS = [
    "channels",
    "channels_postgres",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mozilla_django_oidc",
    "corsheaders",
    "rest_framework",
    "widget_tweaks",
    "dsfr",
    "ami.amidsfr",
    "django.forms",
    "sass_processor",
    "ami.authentication",
    "ami.fi",
    "ami.notification",
    "ami.user",
    "ami.agenda",
    "ami.utils",
    "ami.api",
    "ami.followup",
    "ami.partner",
    "ami.agent",
    "ami.agent_admin",
    "ami.replication",
    # This must come after all the apps, for drf-spectacular to be able to extract endpoints.
    "drf_spectacular",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "ami.authentication.middleware.AMIJWTAuthCookieMiddleware",
    "ami.utils.middleware.TimezoneMiddleware",
]

ROOT_URLCONF = "ami.urls"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [
    BASE_DIR / "public" / "mobile-app" / "build",
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sass_processor.finders.CssFinder",
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
WHITENOISE_ROOT = STATIC_ROOT

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

develop_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
production_loaders = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [STATIC_ROOT],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": develop_loaders if DEBUG else production_loaders,
        },
    },
]

WSGI_APPLICATION = "ami.wsgi.application"
ASGI_APPLICATION = "ami.asgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

postgres_database = dj_database_url.parse(CONFIG["DATABASE_URL"])
data_ware_house = dj_database_url.parse(CONFIG["DATA_WARE_HOUSE_URL"])
DATABASES = {
    "default": postgres_database,
    "channels_postgres": postgres_database,
    "data_ware_house": data_ware_house,
}

# Authentication
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "ami.agent.auth.AgentAuthenticationBackend",
]

LOGIN_URL = "/agent-admin/login/"
LOGIN_REDIRECT_URL = "/agent-admin/"
LOGOUT_REDIRECT_URL = "/agent-admin/"

# Emails
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Tasks
# TODO: use a real task backend in production
TASKS = {"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend"}}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

APPEND_SLASH = False
PUBLIC_APP_URL = CONFIG["PUBLIC_APP_URL"]
PUBLIC_API_URL = CONFIG["PUBLIC_API_URL"]

# Django Rest Framework

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [],  # Set it explicitely to empty, because by default it has basic auth and bypasses our own partner auth decorators.
}
SPECTACULAR_SETTINGS = {
    "TITLE": "AMI API",
    "DESCRIPTION": "API de l'Application Mobile Interminitérielle",
    "VERSION": "1.0.0",
}

# Cors
CORS_ALLOWED_ORIGINS = [PUBLIC_APP_URL]
CORS_ALLOW_CREDENTIALS = True


# Sentry
def before_send(event, hint):
    if "exc_info" in hint:
        _, exc_value, _ = hint["exc_info"]
        if hasattr(exc_value, "status_code") and exc_value.status_code == 401:
            return None
    return event


sentry_sdk.init(
    dsn=CONFIG.get("SENTRY_DSN", ""),
    environment=CONFIG.get("SENTRY_ENV", ""),
    before_send=before_send,  # Filter the exceptions being reported to Sentry.
)

# FranceConnect authentication
AUTH_COOKIE_JWT_NAME = "token"
AUTH_COOKIE_JWT_SECRET = CONFIG["AUTH_COOKIE_JWT_SECRET"]
assert AUTH_COOKIE_JWT_SECRET, "set a random AUTH_COOKIE_JWT_SECRET in your .env.local file"
FC_AMI_CLIENT_ID = CONFIG["FC_AMI_CLIENT_ID"]
FC_AMI_CLIENT_SECRET = CONFIG["FC_AMI_CLIENT_SECRET"]
PUBLIC_FC_BASE_URL = CONFIG["PUBLIC_FC_BASE_URL"]

# This should not be set in production:
# It should be set in the .env.local file for local development
# and in the Scalingo staging and review apps as an env variable.
PUBLIC_FC_PROXY = CONFIG.get("PUBLIC_FC_PROXY")

FC_SCOPE = CONFIG["FC_SCOPE"]
FC_AMI_REDIRECT_URL = PUBLIC_API_URL + "/login-callback"
FC_TOKEN_ENDPOINT = "/api/v2/token"
FC_JWKS_ENDPOINT = "/api/v2/jwks"
FC_USERINFO_ENDPOINT = "/api/v2/userinfo"
FC_AUTHORIZATION_ENDPOINT = "/api/v2/authorize"
FC_LOGOUT_CALLBACK_ENDPOINT = "/api/v2/client/logout-callback"

SECTOR_IDENTIFIER_URL = CONFIG.get("SECTOR_IDENTIFIER_URL", "")

# AMI-FI authentication
USERINFO_COOKIE_JWT_NAME = "ami-fi-userinfo"

# ProConnect authentication
OIDC_RP_SIGN_ALGO = "RS256"
OIDC_RP_CLIENT_ID = CONFIG["PRO_CONNECT_AGENT_ADMIN_CLIENT_ID"]
OIDC_RP_CLIENT_SECRET = CONFIG["PRO_CONNECT_AGENT_ADMIN_CLIENT_SECRET"]
OIDC_OP_AUTHORIZATION_ENDPOINT = CONFIG["PRO_CONNECT_BASE_URL"] + "/api/v2/authorize"
OIDC_OP_TOKEN_ENDPOINT = CONFIG["PRO_CONNECT_BASE_URL"] + "/api/v2/token"
OIDC_OP_JWKS_ENDPOINT = CONFIG["PRO_CONNECT_BASE_URL"] + "/api/v2/jwks"
OIDC_OP_USER_ENDPOINT = CONFIG["PRO_CONNECT_BASE_URL"] + "/api/v2/userinfo"
OIDC_AUTHENTICATION_CALLBACK_URL = "agent-admin:oidc_authentication_callback"
OIDC_RP_SCOPES = "openid email given_name usual_name"
OIDC_OP_LOGOUT_URL_METHOD = "ami.agent.auth.provider_logout"
OIDC_OP_LOGOUT_ENDPOINT = CONFIG["PRO_CONNECT_BASE_URL"] + "/api/v2/session/end"
OIDC_STORE_ID_TOKEN = True

# APi particulier
API_PARTICULIER_BASE_URL = CONFIG["API_PARTICULIER_BASE_URL"]
API_PARTICULIER_QUOTIENT_ENDPOINT = "/v3/dss/quotient_familial/france_connect"
API_PARTICULIER_RECIPIENT_ID = CONFIG["API_PARTICULIER_RECIPIENT_ID"]

# API data.education.gouv
API_DATA_EDUCATION_BASE_URL = CONFIG["API_DATA_EDUCATION_BASE_URL"]
API_DATA_EDUCATION_HOLIDAYS_ENDPOINT = (
    "/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/exports/json"
)


# Partners
PARTNERS_PSL_SECRET = CONFIG.get("PARTNERS_PSL_SECRET", "")
PARTNERS_DINUM_DN_SECRET = CONFIG.get("PARTNERS_DINUM_DN_SECRET", "")
PARTNERS_DINUM_AMI_SECRET = CONFIG.get("PARTNERS_DINUM_AMI_SECRET", "")

# PSL OTV variable
PARTNERS_PSL_OTV_REQUEST_URL = CONFIG.get("PARTNERS_PSL_OTV_REQUEST_URL", "")
PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = CONFIG.get("PARTNERS_PSL_OTV_JWT_CERT_PFX_B64", "")
PARTNERS_PSL_OTV_JWT_CERT_PUBLIC_KEY = CONFIG.get("PARTNERS_PSL_OTV_JWT_CERT_PUBLIC_KEY", "")
PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = CONFIG.get("PARTNERS_PSL_OTV_JWE_PUBLIC_KEY", "")

# Channels
CHANNEL_UNAUTHORIZED_CODE = 4001

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_postgres.core.PostgresChannelLayer",
        "CONFIG": postgres_database,
    }
}

# VAPID keys for webpush
VAPID_APPLICATION_SERVER_KEY = CONFIG["VAPID_APPLICATION_SERVER_KEY"]
VAPID_PUBLIC_KEY = CONFIG["VAPID_PUBLIC_KEY"]
VAPID_PRIVATE_KEY = CONFIG["VAPID_PRIVATE_KEY"]

# Credentials for firebase
GOOGLE_APPLICATION_CREDENTIALS = CONFIG.get("GOOGLE_APPLICATION_CREDENTIALS", "")

# Forms & DSFR
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"
DSFR_USE_INTEGRITY_CHECKSUMS = False

if DEBUG:
    ALLOWED_HOSTS += [
        "localhost",
        "127.0.0.1",
    ]

if sys.argv and sys.argv[0].endswith("pytest"):
    MIDDLEWARE = [m for m in MIDDLEWARE if m != "whitenoise.middleware.WhiteNoiseMiddleware"]

    STORAGES["staticfiles"] = {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }
