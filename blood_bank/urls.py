from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='blood_bank/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request/', views.request_blood, name='request_blood'),
    path('donate/', views.donate_blood, name='donate_blood'),
    path('search/', views.search_donors, name='search'),
    path('manage-request/<int:request_id>/<str:action>/', views.manage_request, name='manage_request'),
    path('manage-donation/<int:donation_id>/<str:action>/', views.manage_donation, name='manage_donation'),
    path('update-stock/', views.update_stock, name='update_stock'),
]

