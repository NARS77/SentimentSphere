from django.contrib import admin
from .models import AnalysisPrompt, AnalysisRun

@admin.register(AnalysisPrompt)
class AnalysisPromptAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'is_default', 'created_at')
    list_filter = ('is_default', 'created_at')
    search_fields = ('name', 'client__username', 'prompt_template')
    raw_id_fields = ('client',)

@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'client', 'status', 'started_at', 'completed_at', 'progress_percentage')
    list_filter = ('status', 'started_at', 'completed_at')
    search_fields = ('batch__name', 'client__username')
    raw_id_fields = ('batch', 'prompt', 'client')
    readonly_fields = ('progress_percentage',)