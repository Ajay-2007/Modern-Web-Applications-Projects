from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drfecommerce.product import views

router = DefaultRouter()

router.register(r"category", views.CategoryViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls))
]

# router is a way of automating withint he process of defining each path