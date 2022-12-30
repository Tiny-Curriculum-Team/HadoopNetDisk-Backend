from utils import *


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
    pass


def search_for_files(request):
    pass


def del_files(request):
    pass
