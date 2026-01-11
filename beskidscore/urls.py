from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT, DEBUG
from django.urls import path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('data.urls')),
    path('api/', include('blog.urls')),
    path('api/auth/', include('users.urls')),
path('api-auth', include('rest_framework.urls')),
]

if DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)