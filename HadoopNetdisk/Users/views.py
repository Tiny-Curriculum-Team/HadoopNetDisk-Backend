import json
from models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings


# Create your views here.
def user_login(request):
    obj = json.loads(request.body)
    username = obj.get('username', None)
    password = obj.get('password', None)

    if username is None or password is None:
        return JsonResponse({'code': 500, 'message': '请求参数错误'})

    is_login = authenticate(request, username=username, password=password)
    if is_login is None:
        return JsonResponse({'code': 500, 'message': '账号或密码错误'})
    login(request, is_login)

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(is_login)
    token = jwt_encode_handler(payload)

    return JsonResponse({'code': 200, 'message': '登录成功', 'data': {'token': token}})


def user_sign_in(request):
    obj = json.loads(request.body)
    user_name = obj.get('username', None)
    password1 = obj.get('password1', None)
    password2 = obj.get('password2', None)
    user_avatar = obj.get('avatar', None)
    user_tele = obj.get('tele', None)
    user_birth = obj.get('birth', None)

    if user_name is None or password1 is None or password2 is None or user_tele is None or user_birth is None:
        return JsonResponse({'code': 500, 'message': '请求参数错误'})
    if password1 != password2:
        return JsonResponse({'code': 500, 'message': '两次密码输入不一致'})
    new_user = User(
        permission_rank=0,
        user_name=user_name,
        available_store=5,
        max_store=5,
        user_avatar=user_avatar,
        user_tele=user_tele,
        user_birth=user_birth
    )
    new_user.save()
    return JsonResponse({'code': 200, 'message': '注册成功'})


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
def get_info(request):
    data = 'some info'
    return JsonResponse({'code': 200, 'message': '请求成功', 'data': data})
