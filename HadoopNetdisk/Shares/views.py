import os
import jwt
import urllib
from Files.utils import *
from Shares.models import Share
from django.conf import settings
from django.http import JsonResponse, FileResponse
from django.contrib.auth.hashers import make_password, check_password


# Create your views here.
def create_sharing(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']

    share_password = request.POST.get("share_password")
    deadline = request.POST.get("deadline")
    file_size = request.POST.get("file_size")

    remote_path = os.path.join(settings.MEDIA_ROOT, "_share_zips", user_name)

    new_sharing = Share.objects.create(
        user_name=user_name,
        share_password=make_password(share_password),
        deadline=deadline,
        file_size=file_size,
        file_path=remote_path,
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
