from django.contrib import admin
from .models import Post, Candidate
from election.models import Election
from core.admin import RemoveDeleteSelectedMixin
from core.admin_filters import ElectionsFilter


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 0


@admin.register(Post)
class PostAdmin(RemoveDeleteSelectedMixin, admin.ModelAdmin):
    list_display = ['id', 'name', 'number', 'election', 'type', 'order']
    inlines = [CandidateInline]
    list_filter = [ElectionsFilter]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if not request.user.is_superuser and db_field.name == 'election':
            kwargs['queryset'] = Election.objects.all().filter(creator=request.user, is_finished=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        base_queryset = Post.objects.all()
        if not request.user.is_superuser:
            return base_queryset.filter(election__creator=request.user)
        return base_queryset

    def has_change_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        if obj.election.has_activated:
            return False
        return obj.election.creator == request.user

    def has_delete_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        if obj.election.has_activated:
            return False
        return obj.election.creator == request.user
