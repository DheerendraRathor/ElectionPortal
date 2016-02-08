from django.contrib import admin

from core.admin import RemoveDeleteSelectedMixin

from .models import Vote


@admin.register(Vote)
class VoteAdmin(RemoveDeleteSelectedMixin, admin.ModelAdmin):
    list_display = ['id', 'candidate', 'vote', 'casted_at']
    list_display_links = None
    list_filter = ['candidate__post__election']
    readonly_fields = ['candidate', 'vote', 'casted_at']

    def get_queryset(self, request):
        qs = Vote.objects.all().order_by('-casted_at')
        if request.user.is_superuser:
            return qs
        return qs.filter(candidate__post__election__is_finished=True,
                         candidate__post__election__creator=request.user)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
