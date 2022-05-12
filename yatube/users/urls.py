from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='registration/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'pass_change/',
        LoginView.as_view(template_name='users/pass_change.html'),
        name='pass_change'
    ),
    path(
        'reset_pass/',
        LoginView.as_view(template_name='users/reset_pass.html'),
        name='reset_pass'
    ),
]
