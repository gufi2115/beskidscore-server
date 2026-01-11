from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from .views import BlogMViewSet, CategoriesViewSet
import beskidscore.settings as settings

router = routers.DefaultRouter()
router.register(r'blog', BlogMViewSet, basename='blog')
router.register(r'categories', CategoriesViewSet, basename='categories')



urlpatterns = [path('',include(router.urls))]
