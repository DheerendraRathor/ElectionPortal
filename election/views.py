import codecs
import csv

from django.contrib import messages
from django.contrib.admin import site
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Case, Count, IntegerField, Prefetch, Sum, When
from django.forms.widgets import SelectMultiple
from django.http.response import Http404
from django.views.generic.base import TemplateView

from account.views import VoterLogoutView
from core.core import IITB_ROLL_REGEX, AlertTags, PostTypes
from post.models import Candidate, Post
from vote.models import Vote

from .models import Election, Tag, Voter
from .serializers import AddVoteSerializer


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
            votes_casted=Sum(Case(When(voters__voted=True, then=1), default=0, output_field=IntegerField()))
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
                         yes_votes=Sum(Case(When(votes__yes=True, then=1), default=0, output_field=IntegerField())),
                         no_votes=Sum(Case(When(votes__no=True, then=1), default=0, output_field=IntegerField())),
                         neutral_votes=Sum(
                             Case(When(votes__neutral=True, then=1), default=0, output_field=IntegerField())),
                     ))
        )

        return super().get(request, *args, posts=posts, **kwargs)


class ElectionView(LoginRequiredMixin, TemplateView):
    template_name = 'elections/election_view.html'

    def _get_next_election(self):
        user = self.request.user
        profile = user.user_profile

        # TODO: This is kinda hack-y. Try to clean it up to make it more scalable
        post_types = [PostTypes.ALL]
        if profile.is_ug:
            post_types.append(PostTypes.UG)
        if profile.is_pg:
            post_types.append(PostTypes.PG)

        election = Election.objects.all().filter(
            is_active=True, is_temporary_closed=False, is_finished=False,
            voters__roll_no__iexact=profile.roll_number, voters__voted=False
        ).prefetch_related(
            Prefetch(
                'posts',
                queryset=Post.objects.all().filter(type__in=post_types).order_by('order').prefetch_related('candidates'),
            ),
            Prefetch('voters', queryset=Voter.objects.all().filter(roll_no__iexact=profile.roll_number),
                     to_attr='voter'),
        ).order_by('id').first()

        self.election = election
        return election

    def get(self, request, *args, **kwargs):
        election = self._get_next_election()

        if not election:
            messages.add_message(request, messages.INFO,
                                 'No election available for you now',
                                 AlertTags.INFO)
            request.method = 'POST'
            return VoterLogoutView.as_view()(request)

        vote_added = kwargs.pop('vote_added', False)
        if vote_added:
            # Uncomment following line to extend session for each election
            # request.session.set_expiry(timedelta(seconds=settings.VOTER_SESSION_TIMEOUT))
            pass

        kwargs['election'] = election
        kwargs['session_timeout'] = request.session.get_expiry_age()

        return super().get(request, *args, **kwargs)

    # TODO: Log errors
    # Todo: Add UG PG validation
    def post(self, request):

        serialized_data = AddVoteSerializer(data=request.body)

        if serialized_data.is_valid():
            election = self._get_next_election()

            if not election or election.pk != serialized_data.validated_data['election']:
                messages.add_message(request, messages.ERROR,
                                     'We got invalid data. This incident is logged',
                                     AlertTags.DANGER)
                return self.get(request)

            # Validate is valid voter
            voters = election.voter
            voter = voters[0]
            if len(voters) != 1:
                messages.add_message(request, messages.ERROR,
                                     'You\'re not a voter.',
                                     AlertTags.DANGER)
                return self.get(request)

            # Validate key
            if election.is_key_required:
                if serialized_data.validated_data['key'] != voter.key:
                    messages.add_message(request, messages.ERROR,
                                         'Invalid Key. This incident is logged',
                                         AlertTags.DANGER)
                    return self.get(request)

            votes = serialized_data.validated_data['votes']
            keys = dict()
            for key, value in votes.items():
                keys[key] = (False, value)

            for post in election.posts.all():
                for candidate in post.candidates.all():
                    if candidate.id not in keys:
                        messages.add_message(request, messages.ERROR,
                                             'Found corrupted data. Incident will be reported',
                                             AlertTags.DANGER)
                        return self.get(request)
                    keys[candidate.id] = (True, keys[candidate.id][1])

            for _, value in keys.items():
                if not value[0]:
                    messages.add_message(request, messages.ERROR,
                                         'Found corrupted data. Incident will be reported',
                                         AlertTags.DANGER)
                    return self.get(request)

            # create voes
            vote_list = []
            for key, value in keys.items():
                vote = Vote(candidate_id=key)
                vote_val = value[1]
                if vote_val == 1:
                    vote.yes = True
                elif vote_val == -1:
                    vote.no = True
                else:
                    vote.neutral = True

                vote_list.append(vote)

            # Add vote to server
            with transaction.atomic():
                Vote.objects.bulk_create(vote_list)
                voter.voted = True
                voter.save()

            messages.add_message(request, messages.INFO, 'Your vote has been recorded', AlertTags.SUCCESS)
            return self.get(request, vote_added=True)
        else:
            messages.add_message(request, messages.INFO,
                                 'Received corrupted data. Incident is recorded',
                                 AlertTags.DANGER)
            return self.get(request)
