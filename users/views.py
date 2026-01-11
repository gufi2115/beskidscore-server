from jwt import InvalidAlgorithmError
from rest_framework import viewsets, mixins, status
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import action
from .serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer, LoginUserSerializer
from rest_framework.views import Response, APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserM
import jwt
from .helpers import decode_token
from beskidscore.settings import SIMPLE_JWT

class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = UserM.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        user = request.user
        if not user or user.is_anonymous:
            return Response(data={'detail': 'Authenticated credentials were not provided'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(self.serializer_class(user).data, status=status.HTTP_200_OK)


class CreateUserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class UpdateUserViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = UpdateUserSerializer
    queryset = UserM.objects.all()
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)



class LoginView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            response = Response(data={'tokens': {'access': access, 'refresh': str(refresh)}, 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
            response.set_cookie(key='access', value=access, httponly=SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                                secure=SIMPLE_JWT['AUTH_COOKIE_SECURE'], samesite=SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
            response.set_cookie(key='refresh', value=str(refresh), httponly=SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                                secure=SIMPLE_JWT['AUTH_COOKIE_SECURE'], samesite=SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
            return response
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                refresh.verify()
                refresh.blacklist()
            except InvalidToken as e:
                return Response({"error": f"Error Invalidation token: {e}"}, status=status.HTTP_401_UNAUTHORIZED)
            except TokenError:
                return Response({"error": f"Error Invalidation token:"}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({"massage": "Successfully logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie(key='access')
        response.delete_cookie(key='refresh')
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token not provided"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = decode_token(refresh_token)
            current_refresh = RefreshToken(refresh_token)
            current_refresh.verify()
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            response = Response({'access': access}, status=status.HTTP_200_OK)
            response.set_cookie(key='access', value=access, httponly=SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                                secure=SIMPLE_JWT['AUTH_COOKIE_SECURE'], samesite=SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
            response.set_cookie(key='refresh', value=str(refresh), httponly=SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                                secure=SIMPLE_JWT['AUTH_COOKIE_SECURE'], samesite=SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
            current_refresh.blacklist()
            return response
        except InvalidToken as e:
            return Response({"error": f"Error Invalidation token: {e}"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.exceptions.DecodeError as e:
            return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_401_UNAUTHORIZED)
        except InvalidAlgorithmError:
            return Response(data={"detail": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.exceptions.ExpiredSignatureError:
            return Response(data={"detail": "Token is expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except TokenError:
            return Response(data={"Error": "Refresh token blacklisted"}, status=status.HTTP_401_UNAUTHORIZED)


            