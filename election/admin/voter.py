import csv

from django.contrib import admin
from django.http.response import HttpResponse

from core.admin import RemoveDeleteSelectedMixin
from core.admin_filters import ElectionsFilter

from ..models import Election, Voter


@admin.register(Voter)
class VoterAdmin(RemoveDeleteSelectedMixin, admin.ModelAdmin):
    list_display = ['roll_no', 'created_at', 'election']
    list_filter = [ElectionsFilter, 'tags']
    search_fields = ['roll_no']
    actions = ['download_voters_action']

    def download_voters_action(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="voters.csv"'
        writer = csv.writer(response)

        queryset = queryset.select_related('election')
        index = 1

        writer.writerow(['S.No.', 'Election Name', 'Voter Roll Number', 'Passkey'])

        for voter in queryset:
            writer.writerow([index, voter.election.name, voter.roll_no, voter.key])
            index += 1

        return response

    download_voters_action.short_description = 'Download voters data'

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        return ['roll_no', 'election', 'tags']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if not request.user.is_superuser and db_field.name == 'election':
            kwargs['queryset'] = Election.objects.all().filter(creator=request.user, is_finished=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        base_queryset = Voter.objects.all()
        if not request.user.is_superuser:
            return base_queryset.filter(election__creator=request.user)
        return base_queryset

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        return request.user.is_superuser or (obj.election.creator == request.user and not obj.election.has_activated)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
