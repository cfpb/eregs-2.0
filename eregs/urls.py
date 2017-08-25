from django.conf.urls import include, url

from eregs_core import urls as eregs_core_urls

urlpatterns = [
    url(r'^$', include(eregs_core_urls, namespace='eregs')),
]
