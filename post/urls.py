from django.conf.urls import url
from .views import CandidateView


urlpatterns = [
    url(r'^get_candidates/$', CandidateView.as_view(), name='get_candidates_verbose'),
]