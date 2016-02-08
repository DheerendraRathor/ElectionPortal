from django.contrib import admin

from core.admin import RemoveDeleteSelectedMixin

from ..models import Tag


@admin.register(Tag)
class TagAdmin(RemoveDeleteSelectedMixin, admin.ModelAdmin):
    list_display = ['tag', 'created_by']
    search_fields = ['tag']

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        return ['tag']

    def has_change_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        return obj.created_by == request.user

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
