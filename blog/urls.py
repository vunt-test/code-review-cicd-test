from django.urls import path

from . import views

urlpatterns = [
    path('api/campaigns/', views.create_campaign, name='create_campaign'),
    path('api/users/', views.users_list_create, name='users_list_create'),
    path('api/users/<int:user_id>/', views.user_detail_update_delete, name='user_detail_update_delete'),
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
]
