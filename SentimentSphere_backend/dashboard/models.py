from django.db import models
from django.contrib.auth.models import User

class FeedbackSource(models.Model):
    """
    Represents a source of feedback (e.g. Google Play, Instagram, etc.)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class FeedbackCategory(models.Model):
    """
    Represents a category for feedback classification (e.g. Positive, Negative, Feature Request)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class FeedbackBatch(models.Model):
    """
    Represents a batch of feedback items uploaded together
    """
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_batches')
    name = models.CharField(max_length=200)
    source = models.ForeignKey(FeedbackSource, on_delete=models.CASCADE, related_name='feedback_batches')
    upload_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    original_file = models.FileField(upload_to='feedback_batches/', blank=True, null=True)
    total_items = models.PositiveIntegerField(default=0)
    keyword_data = models.TextField(blank=True, null=True)
    avg_sentiment = models.FloatField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.upload_date.strftime('%Y-%m-%d')}"

class FeedbackItem(models.Model):
    """
    Represents a single feedback item from a customer
    """
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_items')
    batch = models.ForeignKey(FeedbackBatch, on_delete=models.CASCADE, related_name='feedback_items', null=True, blank=True)
    source = models.ForeignKey(FeedbackSource, on_delete=models.CASCADE, related_name='feedback_items')
    category = models.ForeignKey(FeedbackCategory, on_delete=models.SET_NULL, null=True, related_name='feedback_items')
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(blank=True, null=True)  # For numeric ratings (e.g., 1-5 stars)
    sentiment_score = models.FloatField(blank=True, null=True)  # Sentiment score (-1 to 1)
    processed = models.BooleanField(default=False)  # Whether this feedback has been processed by AI
    customer_id = models.CharField(max_length=100, blank=True, null=True)  # Optional customer identifier
    created_at = models.DateTimeField(auto_now_add=True)
    feedback_date = models.DateTimeField(blank=True, null=True)  # When the feedback was originally given
    
    def __str__(self):
        return f"{self.source.name} - {self.category.name if self.category else 'Uncategorized'}"