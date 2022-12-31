import jwt
import time
import json
import urllib
from Files.utils import *
from Shares.models import Share
from django.conf import settings
from django.forms.models import model_to_dict
from django.http import JsonResponse, FileResponse
from django.contrib.auth.hashers import make_password, check_password


# Create your views here.
def create_sharing(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']
    files = request.FILES.get("files")

    for file_name in files:
        temp_path = os.path.join(settings.MEDIA_ROOT, user_name, file_name)
        with open(temp_path, "wb") as f:
            f.write(file_name)
    zip_file_name = user_name + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.zip'
    remote_path = os.path.join(settings.MEDIA_ROOT, "_share_zips", user_name)
    zip_ya(os.path.join(settings.MEDIA_ROOT, user_name),
           zip_file_name,
           remote_path)

    share_password = request.POST.get("share_password")
    deadline = request.POST.get("deadline")
    file_size = request.POST.get("file_size")

    new_sharing = Share.objects.create(
        user_name=user_name,
        share_password=make_password(share_password),
        deadline=deadline,
        file_size=file_size,
        file_path=os.path.join(remote_path, zip_file_name),
    )
    new_sharing.save()
    return JsonResponse({'code': 200, 'message': '分享成功'})


def del_sharing(request):
    share_id = request.POST.get("share_id")
    share_password = request.POST.get("share_password")

    to_del = Share.objects.get(share_id=share_id)
    file_path = to_del.file_path
    if check_password(share_password, to_del.share_password):
        to_del.delete()
        os.remove(file_path)
        return JsonResponse({'code': 200, 'message': '删除成功'})
    else:
        return JsonResponse({'code': 500, 'message': '密码错误'})


def __download_files(request):
    file_path = request.GET.get('file_path')

    compress_file_name = file_path.split("/")[-1]
    compress_file_path = os.path.join(settings.MEDIA_ROOT, '_share_zips', compress_file_name)

    file = open(compress_file_path, 'rb')
    file_response = FileResponse(file)
    file_response['Content-Type'] = 'application/octet-stream'
    file_response["Access-Control-Expose-Headers"] = 'Content-Disposition'
    file_response['Content-Disposition'] = 'attachment;filename={}'.format(
        urllib.parse.quote(compress_file_name))
    return file_response


def list_shares(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']

    shares = Share.objects.filter(user_name=user_name)
    share_dict = model_to_dict(shares)
    share_dict['code'] = 200
    share_dict['message'] = 'Succeed to list shares.'
    return JsonResponse(json.dumps(share_dict))
