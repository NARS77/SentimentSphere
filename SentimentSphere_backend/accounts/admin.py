from django.contrib import admin
from .models import ClientProfile

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'contact_email', 'created_at')
    search_fields = ('user__username', 'company_name', 'contact_email')
    list_filter = ('created_at',)