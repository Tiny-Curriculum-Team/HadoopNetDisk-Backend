import jwt
import os.path
import urllib.parse

from Files.utils import *
from django.conf import settings
from django.http import FileResponse


def upload_files(request):
    # 接收到formdata的出文件之外的数据
    data = request.POST
    data

    # 接收文件，getlist是接收多个文件
    # formdata在vue中同一个key传入了多个value，value成为了一个数组，所以需要使用getlist来获取所有文件
    new_files = request.FILES.getlist('new_files')

    # formdata在vue中同一个key只有一个文件类型的value，可以使用get来获取文件
    new_files = request.FILES.get('file')





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
