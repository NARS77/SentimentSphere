from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q, F
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import json
import logging
from datetime import timedelta

from .models import FeedbackSource, FeedbackCategory, FeedbackItem, FeedbackBatch
from .serializers import (
    FeedbackSourceSerializer,
    FeedbackCategorySerializer,
    FeedbackItemSerializer,
    FeedbackBatchSerializer
)

logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request):
    """
    Main dashboard view with enhanced summary statistics, trends, and visualizations
    """
    try:
        # Get basic counts with error handling
        total_feedback = FeedbackItem.objects.filter(client=request.user).count()
        processed_feedback = FeedbackItem.objects.filter(client=request.user, processed=True).count()
        total_batches = FeedbackBatch.objects.filter(client=request.user).count()
        
        # Calculate processing percentage safely
        if total_feedback > 0:
            processing_percentage = (processed_feedback / total_feedback) * 100
        else:
            processing_percentage = 0
        
        # Get sentiment distribution with prettier names
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
        ).select_related('source', 'category').order_by('-created_at')[:10]
        
        # Calculate average ratings (only if ratings exist)
        avg_rating = FeedbackItem.objects.filter(
            client=request.user, 
            rating__isnull=False
        ).aggregate(avg=Avg('rating'))
        
        # Calculate average sentiment score
        avg_sentiment = FeedbackItem.objects.filter(
            client=request.user, 
            sentiment_score__isnull=False
        ).aggregate(avg=Avg('sentiment_score'))
        
        # Get counts for different rating levels
        rating_distribution = {}
        for i in range(1, 6):  # Ratings 1-5
            rating_distribution[i] = FeedbackItem.objects.filter(
                client=request.user, 
                rating=i
            ).count()
        
        # Get recent batches
        recent_batches = FeedbackBatch.objects.filter(
            client=request.user
        ).order_by('-upload_date')[:5]
        
        # Calculate trend data for last 7 days
        today = timezone.now().date()
        date_stats = []
        
        for i in range(6, -1, -1):
            target_date = today - timedelta(days=i)
            
            # Get counts for the day
            daily_stats = {
                'date': target_date.strftime('%b %d'),
                'positive': FeedbackItem.objects.filter(
                    client=request.user,
                    category__name='Positive',
                    created_at__date=target_date
                ).count(),
                'negative': FeedbackItem.objects.filter(
                    client=request.user,
                    category__name='Negative',
                    created_at__date=target_date
                ).count(),
                'neutral': FeedbackItem.objects.filter(
                    client=request.user,
                    category__name='Neutral',
                    created_at__date=target_date
                ).count()
            }
            
            date_stats.append(daily_stats)
        
        # Extract keywords from processed feedback (if available)
        # First check if any batches have keyword_data
        top_keywords = []
        try:
            batches_with_keywords = FeedbackBatch.objects.filter(
                client=request.user,
                keyword_data__isnull=False
            ).exclude(keyword_data='').order_by('-upload_date')[:3]
            
            # Combine keywords from recent batches
            for batch in batches_with_keywords:
                try:
                    batch_keywords = json.loads(batch.keyword_data)
                    # Add only if it's a valid list
                    if isinstance(batch_keywords, list):
                        top_keywords.extend(batch_keywords)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Sort and get top keywords
            if top_keywords:
                # Sort by count (descending)
                top_keywords = sorted(top_keywords, key=lambda x: x.get('count', 0), reverse=True)[:16]
        except Exception as e:
            logger.error(f"Error processing keywords: {str(e)}")
            top_keywords = []
        
        # Calculate resolved issues and feature requests (example metrics)
        resolved_issues = {
            'total': FeedbackItem.objects.filter(
                client=request.user, 
                category__name='Bug Report'
            ).count(),
            'resolved': FeedbackItem.objects.filter(
                client=request.user, 
                category__name='Bug Report',
                processed=True
            ).count()
        }
        
        feature_requests = FeedbackItem.objects.filter(
            client=request.user, 
            category__name='Feature Request'
        ).count()
        
        # Calculate average response time (placeholder - customize based on your data model)
        # This assumes you have a response_time or similar field in your model
        avg_response_days = 2.4  # Placeholder value
        
        # Calculate customer satisfaction (based on ratings)
        if avg_rating['avg'] is not None:
            customer_satisfaction = (avg_rating['avg'] / 5) * 100
        else:
            customer_satisfaction = 0
            
        # Combine all data for the template
        context = {
            'total_feedback': total_feedback,
            'processed_feedback': processed_feedback,
            'processing_percentage': processing_percentage,
            'total_batches': total_batches,
            'sentiment_data': list(sentiment_data),
            'source_data': list(source_data),
            'recent_feedback': recent_feedback,
            'avg_rating': avg_rating['avg'] if avg_rating['avg'] is not None else 0,
            'avg_sentiment': avg_sentiment['avg'] if avg_sentiment['avg'] is not None else 0,
            'rating_distribution': rating_distribution,
            'recent_batches': recent_batches,
            'date_stats': date_stats,
            'top_keywords': top_keywords,
            'resolved_issues': resolved_issues,
            'feature_requests': feature_requests,
            'avg_response_days': avg_response_days,
            'customer_satisfaction': customer_satisfaction
        }
        
        return render(request, 'dashboard/dashboard.html', context)
    
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        # Return a simplified dashboard with error messaging
        return render(request, 'dashboard/dashboard.html', {
            'error': True,
            'error_message': "There was an error loading the dashboard. Please try again later."
        })

@login_required
def feedback_list(request):
    """View to list all feedback items with filtering capabilities"""
    # Get all sources and categories for filtering
    sources = FeedbackSource.objects.all()
    categories = FeedbackCategory.objects.all()
    
    # Get query parameters for filtering
    source_id = request.GET.get('source')
    category_id = request.GET.get('category')
    rating = request.GET.get('rating')
    
    # Base queryset
    queryset = FeedbackItem.objects.filter(client=request.user)
    
    # Apply filters if provided
    filters_applied = False
    if source_id:
        queryset = queryset.filter(source_id=source_id)
        filters_applied = True
    if category_id:
        queryset = queryset.filter(category_id=category_id)
        filters_applied = True
    if rating:
        queryset = queryset.filter(rating=rating)
        filters_applied = True
    
    # Get feedback items and paginate
    feedback_items = queryset.select_related('source', 'category').order_by('-created_at')
    
    return render(request, 'dashboard/feedback_list.html', {
        'feedback_items': feedback_items,
        'sources': sources,
        'categories': categories,
        'filters_applied': filters_applied,
        'filtered_count': len(feedback_items) if filters_applied else None
    })

@login_required
def feedback_detail(request, pk):
    """View to show details of a single feedback item with enhanced context"""
    feedback = get_object_or_404(FeedbackItem, pk=pk, client=request.user)
    
    # Get the batch this feedback belongs to
    batch = feedback.batch
    
    # Get similar feedback based on category
    similar_feedback = []
    if feedback.category:
        similar_feedback = FeedbackItem.objects.filter(
            client=request.user,
            category=feedback.category
        ).exclude(id=feedback.id).order_by('-created_at')[:5]
    
    return render(request, 'dashboard/feedback_detail.html', {
        'feedback': feedback,
        'batch': batch,
        'similar_feedback': similar_feedback
    })

@login_required
def batch_list(request):
    """View to list all feedback batches with statistics"""
    # Get all batches with annotated statistics
    batches = FeedbackBatch.objects.filter(client=request.user).annotate(
        item_count=Count('feedback_items'),
        positive_count=Count('feedback_items', filter=Q(feedback_items__category__name='Positive')),
        negative_count=Count('feedback_items', filter=Q(feedback_items__category__name='Negative')),
        avg_sentiment=Avg('feedback_items__sentiment_score')
    ).order_by('-upload_date')
    
    return render(request, 'dashboard/batch_list.html', {
        'batches': batches
    })

@login_required
def batch_detail(request, pk):
    """View to show details of a single batch with comprehensive statistics"""
    batch = get_object_or_404(FeedbackBatch, pk=pk, client=request.user)
    
    # Get feedback items for this batch
    feedback_items = FeedbackItem.objects.filter(
        client=request.user, 
        batch_id=batch.id
    ).select_related('category', 'source')
    
    # Get sentiment distribution
    sentiment_distribution = feedback_items.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get rating distribution
    rating_distribution = {}
    for i in range(1, 6):  # Ratings 1-5
        rating_distribution[i] = feedback_items.filter(rating=i).count()
    
    # Calculate average sentiment score
    avg_sentiment = feedback_items.aggregate(avg=Avg('sentiment_score'))
    
    # Extract keywords if available
    top_keywords = []
    if hasattr(batch, 'keyword_data') and batch.keyword_data:
        try:
            top_keywords = json.loads(batch.keyword_data)
        except json.JSONDecodeError:
            pass
    
    return render(request, 'dashboard/batch_detail.html', {
        'batch': batch,
        'feedback_items': feedback_items,
        'sentiment_distribution': sentiment_distribution,
        'rating_distribution': rating_distribution,
        'avg_sentiment': avg_sentiment['avg'] if avg_sentiment['avg'] is not None else 0,
        'top_keywords': top_keywords
    })

@login_required
def source_list(request):
    """View to list all feedback sources with statistics"""
    # Get all sources with statistics
    sources = FeedbackSource.objects.annotate(
        feedback_count=Count('feedback_items', filter=Q(feedback_items__client=request.user)),
        avg_sentiment=Avg('feedback_items__sentiment_score', filter=Q(feedback_items__client=request.user))
    )
    
    return render(request, 'dashboard/source_list.html', {'sources': sources})

@login_required
def category_list(request):
    """View to list all feedback categories with statistics"""
    # Get all categories with statistics
    categories = FeedbackCategory.objects.annotate(
        feedback_count=Count('feedback_items', filter=Q(feedback_items__client=request.user)),
        avg_sentiment=Avg('feedback_items__sentiment_score', filter=Q(feedback_items__client=request.user))
    )
    
    return render(request, 'dashboard/category_list.html', {'categories': categories})

# API Views with enhanced functionality and better error handling

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_feedback_list(request):
    """API endpoint to get all feedback items for the authenticated user with filters"""
    try:
        # Get query parameters for filtering
        source = request.query_params.get('source')
        category = request.query_params.get('category')
        processed = request.query_params.get('processed')
        rating = request.query_params.get('rating')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
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
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Date range filtering
        if date_from:
            try:
                queryset = queryset.filter(created_at__gte=date_from)
            except ValueError:
                pass  # Ignore invalid date format
                
        if date_to:
            try:
                queryset = queryset.filter(created_at__lte=date_to)
            except ValueError:
                pass  # Ignore invalid date format
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        serializer = FeedbackItemSerializer(queryset, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        logger.error(f"API error in feedback_list: {str(e)}")
        return Response(
            {"error": "An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_stats(request):
    """API endpoint to get comprehensive dashboard statistics"""
    try:
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
        
        # Calculate trend data for last 7 days
        today = timezone.now().date()
        date_stats = []
        
        for i in range(6, -1, -1):
            target_date = today - timedelta(days=i)
            
            # Get counts for the day
            daily_stats = {
                'date': target_date.strftime('%b %d'),
                'positive': FeedbackItem.objects.filter(
                    client=request.user,
                    category__name='Positive',
                    created_at__date=target_date
                ).count(),
                'negative': FeedbackItem.objects.filter(
                    client=request.user,
                    category__name='Negative',
                    created_at__date=target_date
                ).count()
            }
            
            date_stats.append(daily_stats)
        
        # Calculate average rating and sentiment
        avg_stats = FeedbackItem.objects.filter(
            client=request.user
        ).aggregate(
            avg_rating=Avg('rating'),
            avg_sentiment=Avg('sentiment_score')
        )
        
        return Response({
            'total_feedback': total_feedback,
            'processed_feedback': processed_feedback,
            'total_batches': total_batches,
            'sentiment_distribution': list(sentiment_data),
            'source_distribution': list(source_data),
            'date_stats': date_stats,
            'avg_rating': avg_stats['avg_rating'] if avg_stats['avg_rating'] is not None else 0,
            'avg_sentiment': avg_stats['avg_sentiment'] if avg_stats['avg_sentiment'] is not None else 0
        })
        
    except Exception as e:
        logger.error(f"API error in dashboard_stats: {str(e)}")
        return Response(
            {"error": "An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )