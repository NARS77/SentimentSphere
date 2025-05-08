from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Homepage redirect view
def homepage(request):
    return redirect('accounts:login')

urlpatterns = [
    # Add the homepage at the root URL
    path('', homepage, name='homepage'),
    
    # Your existing URLs
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/analysis/', include('analysis.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)