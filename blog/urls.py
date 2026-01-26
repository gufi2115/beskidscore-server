from django.urls import include, path
from rest_framework import routers

from .views import BlogMViewSet, CategoriesViewSet, PhotoViewsSet

router = routers.DefaultRouter()
router.register(r'blog', BlogMViewSet, basename='blog')
router.register(r'categories', CategoriesViewSet, basename='categories')
router.register(r'blog/photo', PhotoViewsSet, basename='photo')

urlpatterns = [path('',include(router.urls))]
