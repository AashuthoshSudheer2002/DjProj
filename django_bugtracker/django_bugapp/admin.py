from django.contrib import admin
from .models import Bug , UserProfile , Sprint
from unfold.admin import ModelAdmin



@admin.register(Bug)
class CustomAdminClass(ModelAdmin):
    list_display = ['title', 'status', 'created_by', 'fixed_by']
    search_fields = ['title', 'info']
    list_filter = ['status']

@admin.register(UserProfile)
class AdminUserProfile(ModelAdmin):
    list_display = ['user','contact_number','bio']
    search_fields = ['user']

@admin.register(Sprint)
class AdminSprintProfile(ModelAdmin):
    list_display = ('name', 'lead_developer', 'developer_list')
    search_fields = ['name']
    def developer_list(self, obj):
        return ", ".join([dev.username for dev in obj.developers.all()])
    developer_list.short_description = "Developers"