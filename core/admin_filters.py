from django.contrib.admin.filters import SimpleListFilter
from election.models import Election


class ElectionsFilter(SimpleListFilter):

    title = 'Elections List'
    parameter_name = 'election_id'

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        if request.user.is_superuser:
            return queryset.filter(election_id=value)
        if value:
            return queryset.filter(election__creator=request.user, election_id=value)

    def lookups(self, request, model_admin):
        base_qs = Election.objects.all().values_list('id', 'name')
        if request.user.is_superuser:
            return base_qs
        return base_qs.filter(creator=request.user)