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
    
    # These might be missing:
    path('batches/<int:pk>/delete/', views.batch_delete, name='batch_delete'),
    path('feedback/<int:pk>/update/', views.feedback_update, name='feedback_update'),
    path('feedback/<int:pk>/delete/', views.feedback_delete, name='feedback_delete'),
    path('feedback/<int:pk>/notes/', views.feedback_notes, name='feedback_notes'),
    path('feedback/<int:pk>/process/', views.feedback_process, name='feedback_process'),
    path('feedback/<int:pk>/export/', views.feedback_export, name='feedback_export'),
    path('batches/export/', views.export_batches, name='export_batches'),
path('feedback/export/', views.export_feedback, name='export_feedback'),]