from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('my-account/', views.my_account, name='my_account'),
    path('profiles/', views.profile_list, name='profile_list'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('biodata/<int:pk>/', views.generate_biodata, name='generate_biodata'),
    path('send-referral-code/', views.send_referral_code, name='send_referral_code'),
]