import csv

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.http.response import HttpResponse
from simple_history.admin import SimpleHistoryAdmin

from core.admin import RemoveDeleteSelectedMixin
from post.models import Post
from post.utils import PostUtils

from ..models import Election
from ..views import AddVotersView, ElectionResultView


class NonSuperuserElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ['creator']


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    show_change_link = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.order_by('order')
        return qs

    def get_max_num(self, request, obj=None, **kwargs):
        if not obj or request.user.is_superuser:
            return super().get_max_num(request, obj, **kwargs)
        if obj.creator != request.user or obj.has_activated:
            return 0

    def get_readonly_fields(self, request, obj=None):
        return PostUtils().get_post_read_only_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        return PostUtils().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return self.has_delete_permission(request, obj)


@admin.register(Election)
class ElectionAdmin(RemoveDeleteSelectedMixin, SimpleHistoryAdmin):
    list_display = ['name', 'creator', 'created_at', 'is_active', 'is_finished']
    list_filter = ['is_active', 'is_finished']
    date_hierarchy = 'created_at'
    inlines = [PostInline]
    actions = ['download_voters_action', 'activate_all']

    def activate_all(self, request, queryset):
        # TODO: Filter by user
        queryset.update(is_active=True)

    activate_all.short_description = 'Activate selected elections'

    def download_voters_action(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="voters.csv"'
        writer = csv.writer(response)

        queryset = queryset.prefetch_related('voters')
        index = 1

        writer.writerow(['S.No.', 'Election Name', 'Voter Roll Number', 'Passkey'])

        for election in queryset:
            for voter in election.voters.all():
                writer.writerow([index, election.name, voter.roll_no, voter.key])
                index += 1

        return response

    download_voters_action.short_description = 'Download voters data'

    def get_readonly_fields(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return []
        read_only_fields = ['creator', 'finished_at']

        if obj.has_activated:
            read_only_fields.append('is_active')
            read_only_fields.append('name')

        if obj.is_finished:
            read_only_fields.append('is_finished')

        return read_only_fields

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        if not obj:
            return ['name']

        if obj.is_finished:
            fields.remove('is_active')
            fields.remove('is_temporary_closed')
        else:
            if not obj.has_activated:
                fields.remove('is_finished')
                fields.remove('is_temporary_closed')
        return fields

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^(.+)/add_voters/$',
                self.admin_site.admin_view(AddVotersView.as_view()), name='election_election_add_voters_url'),
            url(r'^(.+)/get_result/$',
                self.admin_site.admin_view(ElectionResultView.as_view()), name='election_election_get_election_result'),
        ]
        return my_urls + urls

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.creator = request.user
        return super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            kwargs['form'] = NonSuperuserElectionForm
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        base_queryset = Election.objects.all()
        if not request.user.is_superuser:
            return base_queryset.filter(creator=request.user)
        return base_queryset

    def has_change_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        return obj.creator == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj and obj.creator == request.user and not obj.has_activated

    class Media:
        js = ['admin/js/list_filter_collapse.js', ]
