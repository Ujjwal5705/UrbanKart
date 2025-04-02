from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path("", views.dashboard, name="dashboard"),

    path("forgotpassword/", views.forgotpassword, name="forgotpassword"),
    path('validate_password/<uidb64>/<token>/', views.validate_password, name="validate_password"),
    path('reset_password/', views.reset_password, name='reset_password'),
]