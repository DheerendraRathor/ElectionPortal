from django.views.generic import View
from django.http.response import HttpResponse
from .models import Candidate


class CandidateView(View):

    def get(self, request, *args, **kwargs):
        candidates = Candidate.objects.prefetch_related('post__election__creator').values('name', 'post__name',
                                                                                              'post__election__name')
        candid_list = []
        for candidate in candidates:
            candid_list.append('Candidate: %s, Post: %s, Election %s' % (candidate.name, candidate.post.name,
                               candidate.post.election.name))
        return HttpResponse('\n'.join(candid_list), content_type='text/html')

