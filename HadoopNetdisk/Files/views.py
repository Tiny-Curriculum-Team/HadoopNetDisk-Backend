import jwt
import json
import os.path
import urllib.parse
import random
import sys

from Files.utils import *
from django.conf import settings
from django.http import FileResponse, JsonResponse


def upload_files(request):
    # 接收到formdata的出文件之外的数据
    data = request.POST
    token = request.POST.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']
    file_name = data.get('filename')
    file_suffix = data.get('suffix')
    file_path = data.get('path')
    new_file = request.FILES.get('file')

    temp_path = os.path.join(settings.MEDIA_ROOT, user_name, file_name)
    with open(temp_path, "wb") as f:
        f.write(new_file)

    root_path = "http://127.0.0.1:9870/"
    if not (token and user_name and file_name and file_suffix and file_path and new_file):
        return JsonResponse({'code': 500, 'message': '请求参数错误'})
    try:
        hdfs_path = os.path.join(root_path, user_name, file_path)  # 例："http://127.0.0.1:9870/xiaomai/download"
        client_hdfs = connect_to_hdfs()
        upload_to_hdfs(client_hdfs, temp_path, hdfs_path)
    except Exception as e:
        print(e)
        return JsonResponse({'code': 500, 'message': 'hdfs error'})
    try:
        client_hbase = connect_to_hbase()
        if not ("SBhbase" in list_all_tables(client_hbase)):
            create_table(client_hbase, "SBhbase", "fileinfo", "filedata")
            # "fileinfo"                            "filedata"
            # "filename", "suffix", "hdfspath"      "username", "permission", "size"
            insert_a_row(client_hbase, user_name, random.randint(1, 100000), "fileinfo", "filename", file_name)
            insert_a_row(client_hbase, user_name, random.randint(1, 100000), "fileinfo", "suffix", file_suffix)
            insert_a_row(client_hbase, user_name, random.randint(1, 100000), "fileinfo", "hdfspath", hdfs_path)
            insert_a_row(client_hbase, user_name, random.randint(1, 100000), "filedata", "username", user_name)
            insert_a_row(client_hbase, user_name, random.randint(1, 100000), "filedata", "permission", 0)
            insert_a_row(client_hbase, user_name, random.randint(1, 100000), "filedata", "size", sys.getsizeof(new_file))
    except Exception as e:
        print(e)
        return JsonResponse({'code': 500, 'message': 'hbase error'})

    # 接收文件，getlist是接收多个文件
    # formdata在vue中同一个key传入了多个value，value成为了一个数组，所以需要使用getlist来获取所有文件
    # new_files = request.FILES.getlist('new_files')

    # formdata在vue中同一个key只有一个文件类型的value，可以使用get来获取文件
    # new_files = request.FILES.get('file')


def download_files(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']

    file_paths = request.GET.get('file_paths')
    cli = connect_to_hdfs()
    for user_file_path in file_paths:
        file_path = os.path.join('_files', user_file_path)
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
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']
    data = request.POST
    profix = data.get("profix")
    try:
        client_hbase = connect_to_hbase()
        result = find_file(client_hbase,"SBhbase",profix,"filename")
        print(result)
        return JsonResponse(json.dumps(result))
    except Exception as e:
        print(e)
        return JsonResponse({"code": 500, "message": "Error to search"})


def del_files(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']

    file_paths = request.GET.get('file_paths')
    cli = connect_to_hdfs()
    for file_to_del in file_paths:
        try:
            file_path = os.path.join('_files', user_name, file_to_del)
            hdfs_del_files(cli, file_path)
        except Exception as e:
            print(e)
    return JsonResponse({'code': 200, 'message': '删除操作已完成'})


def get_all_files(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']

    request_path = request.GET.get('require_path')

    cli = connect_to_hdfs()
    user_root_dir = os.path.join('_files', user_name, request_path)
    file_dict = hdfs_list(cli, user_root_dir, verbose=True)
    res_dict = {}
    for item in file_dict:
        res_dict.update({item[0]: item[1]['type']})
    res = json.dumps(res_dict)
    return JsonResponse(res)
