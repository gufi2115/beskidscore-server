from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter
from .views import BlogMViewSet, CategoriesViewSet, BlogAttachmentViewSet

router = routers.DefaultRouter()
router.register(r'blog', BlogMViewSet, basename='blog')
router.register(r'categories', CategoriesViewSet, basename='categories')
attachment_router = NestedSimpleRouter(router, r'blog', lookup='blog')
attachment_router.register(r'attachments', BlogAttachmentViewSet, basename='blog-attachment')

urlpatterns = [path('',include(router.urls)),
               path('', include(attachment_router.urls)),]
