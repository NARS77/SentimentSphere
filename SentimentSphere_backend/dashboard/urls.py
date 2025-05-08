from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:pk>/', views.feedback_detail, name='feedback_detail'),
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/<int:pk>/', views.batch_detail, name='batch_detail'),
    path('sources/', views.source_list, name='source_list'),
    path('categories/', views.category_list, name='category_list'),
]