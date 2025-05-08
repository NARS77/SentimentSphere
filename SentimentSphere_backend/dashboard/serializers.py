from rest_framework import serializers
from .models import FeedbackSource, FeedbackCategory, FeedbackItem, FeedbackBatch

class FeedbackSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackSource
        fields = ['id', 'name', 'description']

class FeedbackCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackCategory
        fields = ['id', 'name', 'description']

class FeedbackItemSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = FeedbackItem
        fields = [
            'id', 'client', 'source', 'source_name', 'category', 'category_name', 
            'content', 'rating', 'sentiment_score', 'processed', 
            'customer_id', 'created_at', 'feedback_date'
        ]
        read_only_fields = ['client', 'processed', 'created_at']

class FeedbackBatchSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FeedbackBatch
        fields = [
            'id', 'client', 'name', 'source', 'source_name', 
            'upload_date', 'processed', 'original_file', 'item_count'
        ]
        read_only_fields = ['client', 'upload_date', 'processed']
    
    def get_item_count(self, obj):
        return obj.feedback_items.count()