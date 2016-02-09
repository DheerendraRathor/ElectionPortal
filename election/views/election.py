import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Prefetch
from django.views.generic.base import TemplateView

from account.views import VoterLogoutView
from core.core import LOGGED_IN_SESSION_KEY, AlertTags, PostTypes, VoteTypes
from core.security import get_client_ip
from post.models import Post
from vote.models import Vote
from ..models import Election, Voter
from ..serializers import AddVoteSerializer

logger = logging.getLogger(__name__)


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
                queryset=Post.objects.all().filter(type__in=post_types).order_by('order').prefetch_related(
                    'candidates'),
            ),
            Prefetch('voters', queryset=Voter.objects.all().filter(roll_no__iexact=profile.roll_number),
                     to_attr='voter'),
        ).order_by('id').first()

        self.election = election
        return election

    def get(self, request, *args, **kwargs):
        election = self._get_next_election()

        # Checked if it is landing page after logging in
        logged_in = LOGGED_IN_SESSION_KEY in request.session
        if logged_in:
            del request.session[LOGGED_IN_SESSION_KEY]

        if not election:
            messages.add_message(request, messages.INFO,
                                 'No election available for you now',
                                 AlertTags.INFO)
            request.method = 'POST'
            return VoterLogoutView.as_view()(request)

        new_session = kwargs.pop('new_session', False)
        if new_session or logged_in:
            # Uncomment following line to extend session for each election
            request.session.set_expiry(timedelta(seconds=election.session_timeout))
            pass

        kwargs['election'] = election
        kwargs['session_timeout'] = request.session.get_expiry_age()

        return super().get(request, *args, **kwargs)

    def post(self, request):

        logging_dict = {
            'client_ip': get_client_ip(request),
            'user': request.user,
            'body': request.body[:1024],
            'election': '-1',
        }

        serialized_data = AddVoteSerializer(data=request.body)

        if serialized_data.is_valid():
            election = self._get_next_election()

            if not election:
                logger.error('User has not valid election left', extra=logging_dict)
                messages.add_message(request, messages.ERROR,
                                     'You\'ve no active election. This incident is logged',
                                     AlertTags.DANGER)
                return self.get(request)

            logging_dict['election'] = election.id

            # Validate is valid voter
            voters = election.voter
            voter = voters[0]
            if len(voters) != 1:
                logger.error('User is not a valid voter', extra=logging_dict)
                messages.add_message(request, messages.ERROR,
                                     'You\'re not a voter.',
                                     AlertTags.DANGER)
                return self.get(request)

            # Validate key
            if election.is_key_required:
                if serialized_data.validated_data['key'] != voter.key:
                    logger.error('User has entered invalid key', extra=logging_dict)
                    messages.add_message(request, messages.ERROR,
                                         'Invalid Key. This incident is logged',
                                         AlertTags.DANGER)
                    return self.get(request)

            # Validate votes
            votes = serialized_data.validated_data['votes']
            keys = dict()
            for key, value in votes.items():
                keys[key] = (False, value)

            # Checks that there is a vote for all candidate in election that are visible to voter
            # Like it checks for posts for which voter should be allowed to vote (UG/PG)
            # It also checks if number of non-neutral votes for a post are less then total posts.
            for post in election.posts.all():
                non_neutral_votes = 0
                for candidate in post.candidates.all():
                    if candidate.id not in keys:
                        logger.error('Candidate %s with id %d is missing in user vote', candidate.name, candidate.id,
                                     extra=logging_dict)
                        messages.add_message(request, messages.ERROR,
                                             'Found corrupted data. Incident will be reported',
                                             AlertTags.DANGER)
                        return self.get(request)
                    keys[candidate.id] = (True, keys[candidate.id][1])
                    if keys[candidate.id][1] != VoteTypes.NEUTRAL:
                        non_neutral_votes += 1

                if non_neutral_votes > post.number:
                    logger.error('Number of non-neutral votes are greater than number of posts', extra=logging_dict)
                    messages.add_message(request, messages.ERROR,
                                         'Found invalid data. Attempt is logged',
                                         AlertTags.DANGER)
                    return self.get(request)

            # Check if there is an entry present which are not pk for candidates in election available
            # To person
            for key, value in keys.items():
                if not value[0]:
                    logger.error('User has entered a candidate id %s which is not a valid value', key,
                                 extra=logging_dict)
                    messages.add_message(request, messages.ERROR,
                                         'Found corrupted data. Incident will be reported',
                                         AlertTags.DANGER)
                    return self.get(request)

            # create votes
            vote_list = []
            for key, value in keys.items():
                vote = Vote(candidate_id=key)
                vote.vote = value[1]
                vote_list.append(vote)

            # Add vote to server
            with transaction.atomic():
                Vote.objects.bulk_create(vote_list)
                voter.voted = True
                voter.save()

            messages.add_message(request, messages.INFO, 'Your vote has been recorded', AlertTags.SUCCESS)
            return self.get(request, new_session=True)
        else:
            logger.error('Request data is invalidated by serializer', extra=logging_dict)
            messages.add_message(request, messages.INFO,
                                 'Received corrupted data. Incident is recorded',
                                 AlertTags.DANGER)
            return self.get(request)
