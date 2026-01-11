from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import UserViewSet, CreateUserViewSet, LoginView, LogoutView, \
    CookieTokenRefreshView, UpdateUserViewSet
from django.urls import include, path


router = DefaultRouter()
router.register(r'', UserViewSet)
router.register(r'create-user', CreateUserViewSet, basename='create-user')
router.register(r'update-user', UpdateUserViewSet, basename='update-user')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    path('login/', LoginView.as_view(), name='user-login'),
    path("", include(router.urls))]
