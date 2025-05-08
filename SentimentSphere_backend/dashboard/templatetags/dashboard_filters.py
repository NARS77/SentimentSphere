from django import template

register = template.Library()

@register.filter
def filter_by_category(queryset, category_name):
    """Filter a queryset of FeedbackItems by category name"""
    return queryset.filter(category__name=category_name)

@register.filter
def filter_by_sentiment_range(queryset, range_str):
    """Filter a queryset of FeedbackItems by sentiment score range"""
    try:
        min_val, max_val = map(float, range_str.split(','))
        if min_val < max_val:
            # For a range like 0.2,0.6
            return queryset.filter(sentiment_score__gte=min_val, sentiment_score__lt=max_val)
        else:
            # Edge case - empty result
            return queryset.none()
    except (ValueError, TypeError):
        # If the range string is invalid, return empty queryset
        return queryset.none()