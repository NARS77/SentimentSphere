# In analysis/urls.py
from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('prompts/', views.prompt_list, name='prompt_list'),
    path('prompts/<int:pk>/', views.prompt_detail, name='prompt_detail'),
    path('prompts/<int:pk>/delete/', views.prompt_delete, name='prompt_delete'),
    path('runs/', views.run_list, name='run_list'),
    path('runs/<int:pk>/', views.run_detail, name='run_detail'),
    path('upload/', views.upload_batch, name='upload_batch'),
    path('analyze/<int:batch_id>/', views.analyze_batch, name='analyze_batch'),
    path('download/<int:run_id>/', views.download_results, name='download_results'),
    path('prompts/export/', views.prompt_export, name='prompt_export'),
    path('prompts/import/', views.prompt_import, name='prompt_import'),
    # Added this for the set_default_prompt functionality
    path('prompts/<int:pk>/set-default/', views.set_default_prompt, name='set_default_prompt'),
    path('prompts/<int:pk>/delete/', views.prompt_delete, name='prompt_delete'),
    path('prompts/export/', views.prompt_export, name='prompt_export'),
    path('prompts/import/', views.prompt_import, name='prompt_import'),
    path('prompts/<int:pk>/set-default/', views.set_default_prompt, name='set_default_prompt'),
]