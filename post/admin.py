from django.contrib import admin

from core.admin import RemoveDeleteSelectedMixin
from core.admin_filters import ElectionsFilter
from election.models import Election

from .models import Candidate, Post


class DefaultCandidateInline(admin.TabularInline):
    """
    This inline will keep auto_generate candidates which can't be deleted by normal users
    """
    model = Candidate
    exclude = ['order']
    verbose_name = 'Auto Generated Candidates'
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(auto_generated=True)
        return qs

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ['name', 'image']
        return []

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request).exclude(auto_generated=True)
        return qs

    def get_max_num(self, request, obj=None, **kwargs):
        if not obj or request.user.is_superuser:
            return super().get_max_num(request, obj, **kwargs)
        if obj.election.has_activated:
            return 0

    def get_readonly_fields(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return []
        if obj.election.creator != request.user or obj.election.has_activated:
            return ['name', 'image']
        return []

    def has_delete_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        return not obj.election.has_activated and obj.election.creator == request.user


@admin.register(Post)
class PostAdmin(RemoveDeleteSelectedMixin, admin.ModelAdmin):
    list_display = ['name', 'number', 'election', 'type']
    inlines = [DefaultCandidateInline, CandidateInline]
    list_filter = [ElectionsFilter]

    def get_readonly_fields(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return []
        return ['name', 'number', 'election', 'type', 'order']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if not request.user.is_superuser and db_field.name == 'election':
            kwargs['queryset'] = Election.objects.all().filter(creator=request.user, is_active=False, is_finished=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        base_queryset = Post.objects.all()
        if not request.user.is_superuser:
            return base_queryset.filter(election__creator=request.user)
        return base_queryset

    def has_change_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        return obj.election.creator == request.user

    def has_delete_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        if obj.election.has_activated:
            return False
        return obj.election.creator == request.user
