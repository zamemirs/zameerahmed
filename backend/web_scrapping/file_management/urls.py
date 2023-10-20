from django.urls import path, include
from rest_framework import routers

from file_management.views import UrlsViewSet, LookupKeywordViewSet, WebScrappingViewSet

router = routers.DefaultRouter()
router.register(r"urls", UrlsViewSet, basename="urls")
router.register(r"lookup-keyword", LookupKeywordViewSet, basename="lookup-keyword")
router.register(r'webscraping', WebScrappingViewSet, basename="webscraping")

urlpatterns = [
    path("", include(router.urls)),
]