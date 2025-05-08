from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import FeedbackSource, FeedbackCategory, FeedbackItem, FeedbackBatch
from .serializers import (
    FeedbackSourceSerializer,
    FeedbackCategorySerializer,
    FeedbackItemSerializer,
    FeedbackBatchSerializer
)

@login_required
def dashboard_view(request):
    """
    Main dashboard view with summary statistics
    """
    # Get basic counts
    total_feedback = FeedbackItem.objects.filter(client=request.user).count()
    processed_feedback = FeedbackItem.objects.filter(client=request.user, processed=True).count()
    total_batches = FeedbackBatch.objects.filter(client=request.user).count()
    
    # Get sentiment distribution
    sentiment_data = FeedbackItem.objects.filter(
        client=request.user, 
        processed=True,
        category__isnull=False
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get sources distribution
    source_data = FeedbackItem.objects.filter(
        client=request.user
    ).values('source__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get recent feedback
    recent_feedback = FeedbackItem.objects.filter(
        client=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'total_feedback': total_feedback,
        'processed_feedback': processed_feedback,
        'total_batches': total_batches,
        'sentiment_data': list(sentiment_data),
        'source_data': list(source_data),
        'recent_feedback': recent_feedback,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def feedback_list(request):
    """View to list all feedback items"""
    return render(request, 'dashboard/feedback_list.html')

@login_required
def feedback_detail(request, pk):
    """View to show details of a single feedback item"""
    feedback = get_object_or_404(FeedbackItem, pk=pk, client=request.user)
    return render(request, 'dashboard/feedback_detail.html', {'feedback': feedback})

@login_required
def batch_list(request):
    """View to list all feedback batches"""
    return render(request, 'dashboard/batch_list.html')

@login_required
def batch_detail(request, pk):
    """View to show details of a single batch"""
    batch = get_object_or_404(FeedbackBatch, pk=pk, client=request.user)
    feedback_items = FeedbackItem.objects.filter(client=request.user, batch_id=batch.id)
    
    return render(request, 'dashboard/batch_detail.html', {
        'batch': batch,
        'feedback_items': feedback_items
    })

@login_required
def source_list(request):
    """View to list all feedback sources"""
    sources = FeedbackSource.objects.all()
    return render(request, 'dashboard/source_list.html', {'sources': sources})

@login_required
def category_list(request):
    """View to list all feedback categories"""
    categories = FeedbackCategory.objects.all()
    return render(request, 'dashboard/category_list.html', {'categories': categories})

# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_feedback_list(request):
    """API endpoint to get all feedback items for the authenticated user"""
    # Get query parameters for filtering
    source = request.query_params.get('source')
    category = request.query_params.get('category')
    processed = request.query_params.get('processed')
    
    # Base queryset
    queryset = FeedbackItem.objects.filter(client=request.user)
    
    # Apply filters if provided
    if source:
        queryset = queryset.filter(source_id=source)
    if category:
        queryset = queryset.filter(category_id=category)
    if processed:
        processed_bool = processed.lower() == 'true'
        queryset = queryset.filter(processed=processed_bool)
    
    # Order by creation date (newest first)
    queryset = queryset.order_by('-created_at')
    
    serializer = FeedbackItemSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_feedback_detail(request, pk):
    """API endpoint to get a specific feedback item"""
    try:
        feedback = FeedbackItem.objects.get(pk=pk, client=request.user)
    except FeedbackItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = FeedbackItemSerializer(feedback)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_batch_list(request):
    """API endpoint to get all batches for the authenticated user"""
    batches = FeedbackBatch.objects.filter(client=request.user).order_by('-upload_date')
    serializer = FeedbackBatchSerializer(batches, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_batch_detail(request, pk):
    """API endpoint to get a specific batch"""
    try:
        batch = FeedbackBatch.objects.get(pk=pk, client=request.user)
    except FeedbackBatch.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = FeedbackBatchSerializer(batch)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_source_list(request):
    """API endpoint to get all feedback sources"""
    sources = FeedbackSource.objects.all()
    serializer = FeedbackSourceSerializer(sources, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_category_list(request):
    """API endpoint to get all feedback categories"""
    categories = FeedbackCategory.objects.all()
    serializer = FeedbackCategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_stats(request):
    """API endpoint to get dashboard statistics"""
    # Get basic counts
    total_feedback = FeedbackItem.objects.filter(client=request.user).count()
    processed_feedback = FeedbackItem.objects.filter(client=request.user, processed=True).count()
    total_batches = FeedbackBatch.objects.filter(client=request.user).count()
    
    # Get sentiment distribution
    sentiment_data = FeedbackItem.objects.filter(
        client=request.user, 
        processed=True,
        category__isnull=False
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get sources distribution
    source_data = FeedbackItem.objects.filter(
        client=request.user
    ).values('source__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get average sentiment score over time (last 30 days)
    # This would be more complex in a real application
    
    return Response({
        'total_feedback': total_feedback,
        'processed_feedback': processed_feedback,
        'total_batches': total_batches,
        'sentiment_distribution': list(sentiment_data),
        'source_distribution': list(source_data),
    })