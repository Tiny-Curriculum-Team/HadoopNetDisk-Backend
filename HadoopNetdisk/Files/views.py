import jwt
import os.path
import urllib.parse

from Files.utils import *
from django.conf import settings
from django.http import FileResponse


def upload_files(request):
    pass


def download_files(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']

    file_paths = request.GET.get('file_paths')
    cli = connect_to_hdfs()
    for user_file_path in file_paths:
        file_path = os.path.join('localhost:9870/home/hadoop/_files', user_file_path)
        temp_path = os.path.join(settings.MEDIA_ROOT, user_file_path)
        download_from_hdfs(cli, file_path, temp_path)

    compress_file_name = user_name + '.zip'
    compress_file_path = os.path.join(settings.MEDIA_ROOT, compress_file_name)
    compress_path = os.path.join(settings.MEDIA_ROOT, user_name)
    zip_ya(compress_path, compress_file_name, settings.MEDIA_ROOT)

    file = open(compress_file_path, 'rb')
    file_response = FileResponse(file)
    file_response['Content-Type'] = 'application/octet-stream'
    file_response[
        "Access-Control-Expose-Headers"] = 'Content-Disposition'
    file_response['Content-Disposition'] = 'attachment;filename={}'.format(urllib.parse.quote(compress_file_name))
    return file_response


def search_for_files(request):
    pass


def del_files(request):
    pass
