import Shares.views as views
from django.urls import path

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('openshare/', views.create_sharing),
    path('cancelshare/', views.del_sharing),
    path('getshare/', views.list_shares)
]
