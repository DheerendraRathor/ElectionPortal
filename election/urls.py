from django.conf.urls import url
from .views import ElectionView


urlpatterns = [
    url(r'^$', ElectionView.as_view(), name='index'),
]
