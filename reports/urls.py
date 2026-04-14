from django.urls import path
from .views import auth_page, index, dashboard, logout_view

urlpatterns = [
    path('', auth_page),
    path('home/', index),
    path('dashboard/', dashboard),
    path('logout/', logout_view),
]