from django.contrib import admin
from .models import FeedbackSource, FeedbackCategory, FeedbackItem, FeedbackBatch

@admin.register(FeedbackSource)
class FeedbackSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(FeedbackCategory)
class FeedbackCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(FeedbackItem)
class FeedbackItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'source', 'category', 'rating', 'processed', 'created_at')
    list_filter = ('source', 'category', 'processed', 'created_at')
    search_fields = ('content', 'client__username', 'source__name', 'category__name')
    raw_id_fields = ('client', 'source', 'category')

@admin.register(FeedbackBatch)
class FeedbackBatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'source', 'upload_date', 'processed')
    list_filter = ('source', 'processed', 'upload_date')
    search_fields = ('name', 'client__username', 'source__name')
    raw_id_fields = ('client', 'source')