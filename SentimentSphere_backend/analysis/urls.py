from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('prompts/', views.prompt_list, name='prompt_list'),
    path('prompts/<int:pk>/', views.prompt_detail, name='prompt_detail'),
    path('runs/', views.run_list, name='run_list'),
    path('runs/<int:pk>/', views.run_detail, name='run_detail'),
    path('upload/', views.upload_batch, name='upload_batch'),
    path('analyze/<int:batch_id>/', views.analyze_batch, name='analyze_batch'),
    path('download/<int:run_id>/', views.download_results, name='download_results'),
]