from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTCookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access')
        if not access_token:
            return None
        try:
            validate_token = self.get_validated_token(access_token)
        except Exception:
            return None

        if not validate_token:
            return None

        return self.get_user(validate_token), validate_token
