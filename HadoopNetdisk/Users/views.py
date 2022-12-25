import jwt
from Users.models import User
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password, check_password


# Create your views here.
def user_login(request):
    raw_data = request.POST
    username = raw_data.get("username")
    password = raw_data.get("password")
    if not (username and password):
        return JsonResponse({'code': 500, 'message': '请求参数错误'})
    try:
        user = User.objects.get(user_name=username)
    except Exception as e:
        print("------------------------------------------\n", e, "\n------------------------------------------")
        return JsonResponse({'code': 500, 'message': '用户不存在'})
    else:
        if not check_password(password, user.password):
            return JsonResponse({'code': 500, 'message': '账号或密码错误'})
        else:
            try:
                login(request, user)
                token = jwt.encode({'username': username, 'site': 'netdisk.hadoop.com'},
                                   'secret_key', algorithm='HS256').decode('ascii')
                return JsonResponse({'code': 200, 'message': '登录成功', 'token': token})
            except Exception as e:
                print(e)
                return JsonResponse({'code': 500, 'message': '请求错误'})


def user_sign_in(request):
    if request.method == 'POST':
        raw_data = request.POST
        user_name = raw_data.get("username")
        password1 = raw_data.get("password1")
        password2 = raw_data.get("password2")
        user_avatar = raw_data.get("avatar")
        user_tele = raw_data.get("tele")
        user_birth = raw_data.get("birth")

        if not (user_name and password1 and password2 and user_tele and user_birth):
            return JsonResponse({'code': 500, 'message': '请求参数错误'})
        elif password1 != password2:
            return JsonResponse({'code': 500, 'message': '两次密码输入不一致'})
        else:
            try:
                new_user = User(
                    permission_rank=0,
                    user_name=user_name,
                    password=make_password(password1),
                    available_store=5,
                    max_store=5,
                    user_avatar=user_avatar,
                    user_tele=user_tele,
                    user_birth=user_birth
                )
                new_user.save()
            except Exception as e:
                print("------------------------------------------\n", e, "\n------------------------------------------")
                return JsonResponse({'code': 500, 'message': '请求错误，可能是用户名已被使用'})
            return JsonResponse({'code': 200, 'message': '注册成功'})
