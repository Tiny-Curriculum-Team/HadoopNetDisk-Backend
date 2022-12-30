import Files.views as views
from django.urls import path

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('upload/, ', views.upload_files),
    path('download/, ', views.download_files),
    path('delfile/, ', views.del_files),
    path('search/, ', views.search_for_files),
]
