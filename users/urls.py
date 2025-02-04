from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name='user-register'),
    path('login/', login_view, name='user-log-in'),
    path('logout/', login_view, name='user-logout'),
]