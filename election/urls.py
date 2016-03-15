from django.conf.urls import url
from django.contrib.admin import site

from .views import ElectionPreview, ElectionView, ElectionDocsView

ElectionPreviewView = site.admin_view(ElectionPreview.as_view())
ElectionDocsView = site.admin_view(ElectionDocsView.as_view())


urlpatterns = [
    url(r'^$', ElectionView.as_view(), name='index'),
    url(r'^preview/(?P<pk>\d+)/$', ElectionPreviewView, name='preview'),
    url(r'^preview/(?P<pk>\d+)/(?P<type>[up]g)/$', ElectionPreviewView, name='preview'),
    url(r'doc/$', ElectionDocsView, name='docs'),
]
