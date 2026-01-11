import jwt
from .models import UserM
from beskidscore.settings import SECRET_KEY as secret_key

def decode_token(token):
    decode_token = jwt.decode(token, secret_key, algorithms=["HS256"])
    user_id = decode_token['user_id']
    user_obj = UserM.objects.get(id=user_id)
    return user_obj
