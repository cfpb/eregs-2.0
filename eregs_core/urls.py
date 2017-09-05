from django.conf.urls import url

from eregs_core.views import (
    definition_partial, diff, diff_partial, diff_redirect, regulation,
    regulation_main, regulation_partial, search, search_partial,
    sidebar_partial, sxs_partial
)
from eregs_core.views.main import MainView


urlpatterns = [
    url(r'^$', MainView.as_view(), name='eregs_main'),
    url(r'^(?P<part_number>[\d]{4})',
        regulation_main,
        name='eregs_regulation_main'),
    url((
            r'^regulation/'
            '(?P<version>[\d]+-[\d]+)/'
            '(?P<eff_date>[\d]{4}-[\d]{2}-[\d]{2})/'
            '(?P<node>.*)$'
        ),
        regulation,
        name='eregs_regulation'),
    url((
            r'^diff_redirect/'
            '(?P<left_version>[\d]+-[\d]+)/'
            '(?P<left_eff_date>[\d]{4}-[\d]{2}-[\d]{2})/'
        ),
        diff_redirect,
        name='eregs_diff_redirect'),
    url(r'^search/$', search, name='eregs_search'),
    url((
            r'^diff/(?P<left_version>[\d]+-[\d]+)/'
            '(?P<left_eff_date>[\d]{4}-[\d]{2}-[\d]{2})/'
            '(?P<right_version>[\d]+-[\d]+)/'
            '(?P<right_eff_date>[\d]{4}-[\d]{2}-[\d]{2})/'
            '(?P<node>.*)$'
        ),
        diff,
        name='eregs_diff'),
    url(r'^partial/diff/(?P<left_version>[\d]+-[\d]+)/(?P<left_eff_date>[\d]{4}-[\d]{2}-[\d]{2})/'
        r'(?P<right_version>[\d]+-[\d]+)/(?P<right_eff_date>[\d]{4}-[\d]{2}-[\d]{2})/(?P<node>.*)$', diff_partial),
    url(r'^partial/(?P<version>[\d]+-[\d]+)/(?P<eff_date>[\d]{4}-[\d]{2}-[\d]{2})/(?P<node>.*)$', regulation_partial),
    url((
        r'^partial/sxs/'
        '(?P<version>[\d]+-[\d]+)/'
        '(?P<eff_date>[\d]{4}-[\d]{2}-[\d]{2})/'
        '(?P<node>.*)$'
        ),
        sxs_partial,
        name='eregs_sxs_partial'),
    url(r'^partial/sidebar/(?P<version>[\d]+-[\d]+)/(?P<eff_date>[\d]{4}-[\d]{2}-[\d]{2})/(?P<node>.*)$', sidebar_partial),
    url(r'^partial/definition/(?P<version>[\d]+-[\d]+)/(?P<eff_date>[\d]{4}-[\d]{2}-[\d]{2})/(?P<node>.*)$', definition_partial),
    url(r'^partial/search/$', search_partial, name='eregs_partial_search'),
]

