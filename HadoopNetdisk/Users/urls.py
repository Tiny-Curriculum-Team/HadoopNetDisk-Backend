import views
from django.urls import path

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/', views.user_login),
    path('signin/', views.user_sign_in),
]
