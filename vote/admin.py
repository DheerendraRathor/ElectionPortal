from django.contrib import admin
from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'candidate', 'yes', 'no', 'neutral']
    list_display_links = None
    readonly_fields = Vote._meta.get_all_field_names()

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
