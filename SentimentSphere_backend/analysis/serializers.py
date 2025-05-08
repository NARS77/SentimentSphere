from rest_framework import serializers
from .models import AnalysisPrompt, AnalysisRun
from dashboard.serializers import FeedbackBatchSerializer

class AnalysisPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisPrompt
        fields = [
            'id', 'name', 'client', 'prompt_template', 
            'description', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['client', 'created_at', 'updated_at']

class AnalysisRunSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    prompt_name = serializers.CharField(source='prompt.name', read_only=True)
    batch_details = FeedbackBatchSerializer(source='batch', read_only=True)
    
    class Meta:
        model = AnalysisRun
        fields = [
            'id', 'batch', 'batch_name', 'prompt', 'prompt_name', 
            'client', 'status', 'started_at', 'completed_at',
            'total_items', 'processed_items', 'progress_percentage',
            'error_message', 'batch_details'
        ]
        read_only_fields = [
            'client', 'status', 'started_at', 'completed_at',
            'total_items', 'processed_items', 'progress_percentage', 'error_message'
        ]