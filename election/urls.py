from django.conf.urls import url
from django.contrib.admin import site

from .views import ElectionPreview, ElectionView

ElectionPreviewView = site.admin_view(ElectionPreview.as_view())


urlpatterns = [
    url(r'^$', ElectionView.as_view(), name='index'),
    url(r'^preview/(?P<pk>\d+)/$', ElectionPreviewView, name='preview'),
    url(r'^preview/(?P<pk>\d+)/(?P<type>[up]g)/$', ElectionPreviewView, name='preview'),
]
