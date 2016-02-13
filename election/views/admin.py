"""
This file contains election views which requires admin permission and are related to admin
1. Add Voters View (AddVotersView)
2. Election Results (ElectionResultView)
3. Election Preview (ElectionPreview)
"""
import codecs
import csv

from django.contrib import messages
from django.contrib.admin import site
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db import transaction
from django.db.models import Case, Count, IntegerField, Prefetch, Sum, When
from django.forms.widgets import SelectMultiple
from django.http.response import Http404
from django.views.generic.base import TemplateView

from core.core import IITB_ROLL_REGEX, POST_TYPE_DICT, AlertTags, PostTypes, VoteTypes
from post.models import Candidate, Post

from ..models import Election, Tag, Voter
from .election import ElectionView


class AddVotersView(TemplateView):
    template_name = 'elections/add_voters.html'

    def _validate_args(self, request, *args):
        if len(args) < 1:
            raise Http404

        qs = Election.objects.all().filter(pk=args[0])

        if not request.user.is_superuser:
            qs = qs.filter(creator=request.user, is_finished=False)

        if len(qs) > 0:
            self.object = qs[0]
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        kwargs['opts'] = Election._meta
        kwargs['object'] = self.object
        kwargs['title'] = 'Add Voters List'
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self._validate_args(request, *args)

        tags = Tag.objects.all().values_list('id', 'tag')

        tags_list = SelectMultiple(choices=tags)
        voter_opts = Voter._meta
        tag_field = voter_opts.many_to_many[0]
        model_admin = site._registry[Voter]
        admin_tags_list = RelatedFieldWidgetWrapper(
            tags_list,
            tag_field.remote_field,
            site,
            True,
            False,
            False)
        media = model_admin.media
        kwargs['media'] = media
        kwargs['tags_related'] = admin_tags_list.render('tags', None, attrs={
            'id': 'id_tags',
        })
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._validate_args(request, *args)

        file = request.FILES.get('voters_list', None)
        roll_column = request.POST.get('roll_col', 0)
        skip_one_row = 'skip_one_row' in request.POST
        skip_errors = 'skip_errors' in request.POST
        tags_list = request.POST.getlist('tags', [])

        tags = Tag.objects.all().filter(pk__in=tags_list)

        if len(tags) != len(tags_list):
            messages.add_message(self.request, messages.ERROR, 'Invalid tags found. Aborted.')
            return self.get(self.request, *args, **kwargs)

        if len(tags) > 5:
            messages.add_message(self.request, messages.ERROR, 'Maximum 5 tags are allowed')
            return self.get(self.request, *args, **kwargs)

        if not file:
            messages.add_message(self.request, messages.ERROR, 'File can not be empty')
            return self.get(self.request, *args, *kwargs)
        try:
            roll_column = int(roll_column)
        except ValueError:
            messages.add_message(self.request, messages.ERROR, 'Roll Columns must be an integer')
            return self.get(self.request, *args, *kwargs)

        reader = csv.reader(codecs.iterdecode(file, 'utf-8'), delimiter=',')
        index = 0
        new_voters_added = 0
        message = ''

        try:
            with transaction.atomic():
                voter_list = []
                for row in reader:
                    index += 1
                    if skip_one_row and index == 1:  # First Row
                        continue

                    try:
                        roll_number = row[roll_column]
                    except IndexError:
                        if not skip_errors:
                            message = 'Invalid line found in data at line number %d : %s' % (index, ','.join(row))
                            raise
                        else:
                            continue

                    if not IITB_ROLL_REGEX.match(roll_number):
                        if skip_errors:
                            continue
                        else:
                            message = 'Roll number %s in line %d is not a valid roll number' % (roll_number, index)
                            raise ValueError

                    roll_number = roll_number.upper()

                    # TODO: This is definitely not the best way. But Checking for uniqueness is a pain
                    voter, created = Voter.objects.get_or_create(roll_no=roll_number, election=self.object)
                    if created:
                        new_voters_added += 1
                    voter_list.append(voter)

                for tag in tags:
                    tag.voter_set.add(*voter_list)

        except (IndexError, ValueError):
            messages.add_message(self.request, messages.ERROR, message)
        else:
            total_voters = Voter.objects.all().filter(election=self.object).count()
            messages.add_message(self.request, messages.SUCCESS,
                                 '%s new voters added. Total voters for this election = %d' % (new_voters_added,
                                                                                               total_voters))

        return self.get(self.request, *args, **kwargs)


class ElectionResultView(TemplateView):
    template_name = 'elections/display_results.html'

    def _validate_args(self, request, *args):
        if len(args) < 1:
            raise Http404
        queryset = Election.objects.all().annotate(
            total_voters=Count('voters'),
        ).filter(pk=args[0])

        if not request.user.is_superuser:
            queryset = queryset.filter(creator=request.user, is_finished=True)

        if len(queryset) > 0:
            self.object = queryset[0]
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        kwargs['opts'] = Election._meta
        kwargs['object'] = self.object
        kwargs['title'] = 'Election Results'
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self._validate_args(request, *args)

        posts = Post.objects.all().filter(election=self.object).prefetch_related(
            Prefetch('candidates',
                     queryset=Candidate.objects.all().annotate(
                         yes_votes=Sum(
                             Case(When(votes__vote=VoteTypes.YES, then=1), default=0, output_field=IntegerField())),
                         no_votes=Sum(
                             Case(When(votes__vote=VoteTypes.NO, then=1), default=0, output_field=IntegerField())),
                     ))
        )

        return super().get(request, *args, posts=posts, **kwargs)


class ElectionPreview(ElectionView):
    template_name = 'elections/election_view.html'

    def _get_next_election(self):
        election_id = self.kwargs['pk']
        view_as = self.kwargs.get('type', '').upper()

        post_types = [PostTypes.ALL]
        if view_as == POST_TYPE_DICT[PostTypes.UG]:
            post_types.append(PostTypes.UG)
        if view_as == POST_TYPE_DICT[PostTypes.PG]:
            post_types.append(PostTypes.PG)

        election = Election.objects.all().filter(pk=election_id).prefetch_related(
            Prefetch(
                'posts',
                queryset=self._get_base_post_qs(post_types=post_types)
            )
        ).order_by('id')

        if not self.request.user.is_superuser:
            election = election.filter(creator=self.request.user)

        election = election.first()

        messages.add_message(self.request, messages.INFO, 'Election Preview', AlertTags.INFO)

        self.election = election
        return election

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.ERROR, 'Cannot cast vote in election preview.', AlertTags.DANGER)
        return self.get(request)
