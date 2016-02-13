from django.contrib import admin

from core.admin import RemoveDeleteSelectedMixin

from .models import Vote, VoteSession


class VoteInline(admin.TabularInline):
    readonly_fields = ['candidate', 'vote']
    model = Vote

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VoteSession)
class VoteSessionAdmin(RemoveDeleteSelectedMixin, admin.ModelAdmin):
    inlines = [VoteInline]
    date_hierarchy = 'timestamp'


@admin.register(Vote)
class VoteAdmin(RemoveDeleteSelectedMixin, admin.ModelAdmin):
    list_display = ['id', 'candidate', 'vote', ]
    list_display_links = None
    list_filter = ['candidate__post__election']
    readonly_fields = ['candidate', 'vote', ]

    def get_queryset(self, request):
        qs = Vote.objects.all()
        if request.user.is_superuser:
            return qs
        return qs.filter(candidate__post__election__is_finished=True,
                         candidate__post__election__creator=request.user)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
