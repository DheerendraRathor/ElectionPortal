from django.conf.urls import url
from django.contrib import admin

from post.models import Post
from .models import Election, Voter
from .forms import NonSuperuserElectionForm
from .views import AddVotersView, ElectionResultView
from simple_history.admin import SimpleHistoryAdmin
from post.utils import PostUtils
from core.admin import RemoveDeleteSelectedMixin


class PostInline(admin.TabularInline):
    model = Post
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        return PostUtils().get_post_read_only_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        return PostUtils().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return self.has_delete_permission(request, obj)


@admin.register(Election)
class ElectionAdmin(RemoveDeleteSelectedMixin, SimpleHistoryAdmin):
    list_display = ['name', 'creator', 'created_at', 'is_active', 'is_finished']
    inlines = [PostInline]

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


@admin.register(Voter)
class VoterAdmin(RemoveDeleteSelectedMixin, admin.ModelAdmin):
    list_display = ['roll_no', 'created_at', 'election']
    list_filter = ['election']
    search_fields = ['roll_no']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        return ['roll_no', 'election']

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
