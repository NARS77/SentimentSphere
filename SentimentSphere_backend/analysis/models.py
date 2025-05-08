from django.db import models
from django.contrib.auth.models import User
from dashboard.models import FeedbackBatch

class AnalysisPrompt(models.Model):
    """
    Represents a custom prompt template for OpenAI API
    """
    name = models.CharField(max_length=100)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_prompts')
    prompt_template = models.TextField(help_text="Template for the prompt to be sent to OpenAI. Use {feedback} as placeholder for the feedback text.")
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.client.username}"

class AnalysisRun(models.Model):
    """
    Represents a single run of analysis on a batch of feedback
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    batch = models.ForeignKey(FeedbackBatch, on_delete=models.CASCADE, related_name='analysis_runs')
    prompt = models.ForeignKey(AnalysisPrompt, on_delete=models.SET_NULL, null=True, related_name='analysis_runs')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_runs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    total_items = models.PositiveIntegerField(default=0)
    processed_items = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Run {self.id} - {self.batch.name} - {self.status}"
    
    @property
    def progress_percentage(self):
        if self.total_items == 0:
            return 0
        return int((self.processed_items / self.total_items) * 100)