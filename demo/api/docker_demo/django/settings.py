from importlib import metadata

from model_w.env_manager import EnvManager
from model_w.preset.django import ModelWDjango

# Variables set by the EnvManager but declared here so IDEs don't complain
DEBUG = False
MIDDLEWARE = []
REST_FRAMEWORK = {}


def get_package_version() -> str:
    """
    Trying to get the current package version using the metadata module. This
    assumes that the version is indeed set in pyproject.toml and that the
    package was cleanly installed.
    """
    try:
        return metadata.version("docker_demo")
    except metadata.PackageNotFoundError:
        return "0.0.0"


with EnvManager(ModelWDjango()) as env:
    # ---
    # Apps
    # ---

    INSTALLED_APPS = [
        "drf_spectacular",
        "drf_spectacular_sidecar",
        "docker_demo.apps.realtime",
        "procrastinate.contrib.django",
        "docker_demo.apps.people",
        "docker_demo.apps.health",
    ]

    # ---
    # Plumbing
    # ---

    ROOT_URLCONF = "docker_demo.django.urls"

    WSGI_APPLICATION = "docker_demo.django.wsgi.application"
    ASGI_APPLICATION = "docker_demo.django.asgi.application"

    # ---
    # Auth
    # ---

    AUTH_USER_MODEL = "people.User"

    # ---
    # i18n
    # ---

    LANGUAGES = [
        ("en", "English"),
    ]

    # ---
    # Logging
    # ---
    MIDDLEWARE.append(
        "docker_demo.django.middleware.RequestLogMiddleware"
    )

    # ---
    # OpenAPI Schema
    # ---

    REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"

    SPECTACULAR_SETTINGS = {
        "TITLE": "Docker Demo",
        "VERSION": get_package_version(),
        "SERVE_INCLUDE_SCHEMA": False,
        "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
        "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
        "REDOC_DIST": "SIDECAR",
    }


    if DEBUG:
        # Django Debug Toolbar
        INSTALLED_APPS.append("debug_toolbar")
        MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
        INTERNAL_IPS = [
            "127.0.0.1",
        ]
        DEBUG_TOOLBAR_CONFIG = {
            "SHOW_COLLAPSED": True,
        }

        # Django Extensions
        INSTALLED_APPS.append("django_extensions")
