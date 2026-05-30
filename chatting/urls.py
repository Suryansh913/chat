from django.contrib import admin
from django.urls import path, include
from chat.views import index
from auth_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.register_view, name='register'),
    path('chat/', index, name='index'),
    path('auth/', include('auth_app.urls')),
]