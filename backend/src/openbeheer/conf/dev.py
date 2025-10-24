import os
import warnings

from corsheaders.defaults import default_headers

from .utils import config

os.environ.setdefault("DEBUG", "yes")
os.environ.setdefault("ALLOWED_HOSTS", "*")
os.environ.setdefault(
    "SECRET_KEY",
    "django-insecure-s2@4$0-hicntn)29@5g@!vnw6ovh#dtj!w6)$79rhs&l9==kac",
)
os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("VERSION_TAG", "dev")

os.environ.setdefault("DB_NAME", "openbeheer")
os.environ.setdefault("DB_USER", "openbeheer")
os.environ.setdefault("DB_PASSWORD", "openbeheer")

os.environ.setdefault("ENVIRONMENT", "development")

from .base import *  # noqa isort:skip

# Feel free to switch dev to sqlite3 for simple projects,
# os.environ.setdefault("DB_ENGINE", "django.db.backends.sqlite3")

#
# Standard Django settings.
#
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING["loggers"].update(
    {
        "openbeheer": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["django"],
            "level": "DEBUG",
            "propagate": False,
        },
        "performance": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "vcr": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        #
        # See: https://code.djangoproject.com/ticket/30554
        # Autoreload logs excessively, turn it down a bit.
        #
        "django.utils.autoreload": {
            "handlers": ["django"],
            "level": "INFO",
            "propagate": False,
        },
    }
)

SESSION_ENGINE = "django.contrib.sessions.backends.db"

# in memory cache and django-axes don't get along.
# https://django-axes.readthedocs.io/en/latest/configuration.html#known-configuration-problems
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "axes": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
}

#
# Library settings
#

ELASTIC_APM["DEBUG"] = True

#
# Django CORS-headers
#

# In development, the backend and the frontend don't run on the same port
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"] + MIDDLEWARE

# This is reflected in the access-control-allow-origin header
# An origin is the scheme (http/https) + the domain name + port number
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", split=True, default=[])
CORS_ALLOWED_ORIGIN_REGEXES = config(
    "CORS_ALLOWED_ORIGIN_REGEXES", split=True, default=[]
)
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=False)

# This is reflected in the Access-Control-Allow-Headers response header.
# It is used in response to a preflight request to indicate which headers can be included in the actual request.
CORS_EXTRA_ALLOW_HEADERS = config("CORS_EXTRA_ALLOW_HEADERS", split=True, default=[])
CORS_ALLOW_HEADERS = (
    *default_headers,
    *CORS_EXTRA_ALLOW_HEADERS,
)

# Reflected in the Access-Control-Expose-Headers header
# Specifies which response headers are exposed to JS in cross-origin requests.
CORS_EXPOSE_HEADERS = ["X-CSRFToken"]

# Reflected in the Access-Control-Allow-Credentials header.
# This response header tells the browser whether to expose the response to the JS when the request's credentials mode
# is 'include'. When used in a preflight response, it tells whether to send credentials (in our case, the cookies).
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    split=True,
    default=[],
)

# Django debug toolbar
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
INTERNAL_IPS = ("127.0.0.1",)


# None of the authentication backends require two-factor authentication.
if config("DISABLE_2FA", default=False):
    MAYKIN_2FA_ALLOW_MFA_BYPASS_BACKENDS = AUTHENTICATION_BACKENDS

# THOU SHALT NOT USE NAIVE DATETIMES
warnings.filterwarnings(
    "error",
    r"DateTimeField .* received a naive datetime",
    RuntimeWarning,
    r"django\.db\.models\.fields",
)

# Playwright settings
E2E_TESTS = config("E2E_TESTS", default=True)

# Override settings with local settings.
try:  # noqa: SIM105
    from .local import *  # noqa
except ImportError:
    pass
