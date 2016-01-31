import codecs
import csv

from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Count, Sum, Case, When, IntegerField
from django.http.response import Http404
from django.views.generic.base import TemplateView

from core.core import IITB_ROLL_REGEX
from post.models import Post, Candidate
from .models import Election, Voter


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
        self._validate_args(*args)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._validate_args(*args)

        file = request.FILES.get('voters_list', None)
        roll_column = request.POST.get('roll_col', 0)
        skip_one_row = 'skip_one_row' in request.POST
        skip_errors = 'skip_errors' in request.POST

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

                    _, created = Voter.objects.get_or_create(roll_no=roll_number, election=self.object)
                    if created:
                        new_voters_added += 1

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


