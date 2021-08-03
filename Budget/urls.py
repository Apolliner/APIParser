from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Budget import views

router = DefaultRouter()
router.register(r'uploadedAPI', views.UploadedAPIViewSet)

urlpatterns = [
    path('', include(router.urls)),
]