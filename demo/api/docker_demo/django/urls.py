from importlib import metadata

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from ninja import NinjaAPI

from docker_demo.apps.people.api import router as people_router

admin.site.site_title = _("Docker Demo")
admin.site.site_header = _("Docker Demo")

api = NinjaAPI(
    title="Docker Demo API",
    version=metadata.version("docker_demo"),
    docs_url=(settings.DEBUG and "/docs") or "",
    openapi_url=(settings.DEBUG and "/openapi.json") or "",
)

api.add_router("/me", people_router)

urlpatterns = [
    path("back/_/ht/", include("docker_demo.apps.health.urls")),
    path("back/admin/", admin.site.urls),
    path("back/api/", api.urls),
]

if settings.DEBUG:
    urlpatterns += [
        path("back/__debug__/", include("debug_toolbar.urls")),
    ]
