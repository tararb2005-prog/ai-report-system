from django.contrib import admin
from django.urls import path
from reports import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.auth_page),
    path('home/', views.index),
    path('dashboard/', views.dashboard),
    path('logout/', views.logout_view),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)