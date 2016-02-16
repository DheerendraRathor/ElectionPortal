import csv

from django.contrib import admin
from django.http import HttpResponse

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
    list_filter = ['election']
    list_display = ['id', 'timestamp', 'election', ]

    actions = ['download_data']

    def download_data(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="votes_data.csv"'
        writer = csv.writer(response)

        queryset = queryset.select_related('election')
        index = 1

        writer.writerow(['S.No.', 'Election Name', 'Timestamp', ])

        for session in queryset:
            writer.writerow([index, session.election.name, session.timestamp])
            index += 1

        return response

    download_data.short_description = 'Download voting data'


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
