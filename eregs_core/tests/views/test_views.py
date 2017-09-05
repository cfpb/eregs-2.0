import os

from django.conf import settings
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from mock import Mock, patch

from eregs_core.views import (
    definition_partial, regulation, regulation_main, regulation_partial,
    search, search_partial, sidebar_partial
)


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()

        cls.effective_date = '2011-12-30'
        cls.version = '2011-31712'
        cls.dated_version = ':'.join([cls.version, cls.effective_date])

        filename = os.path.join(settings.DATA_DIR, cls.version + '.xml')
        call_command('import_xml', filename)

        cls.patched_sqs = patch(
            'eregs_core.views.SearchQuerySet',
            filter=Mock(return_value=[])
        )
        cls.patched_sqs.start()

    @classmethod
    def tearDownClass(cls):
        cls.patched_sqs.stop()
        super(TestViews, cls).tearDownClass()

    def request(self, **kwargs):
        return RequestFactory().get('/', kwargs)

    def test_view_definition_partial(self):
        response = definition_partial(
            self.request(),
            self.version,
            self.effective_date,
            '1003-A'
        )
        self.assertEquals(response.status_code, 200)

    def test_view_regulation(self):
        response = regulation(
            self.request(),
            self.version,
            self.effective_date,
            '1003-A'
        )
        self.assertEquals(response.status_code, 200)

    def test_view_regulation_main(self):
        response = regulation_main(self.request(), 1003)
        self.assertEquals(response.status_code, 200)

    def test_view_regulation_partial(self):
        response = regulation_partial(
            self.request(),
            self.version,
            self.effective_date,
            '1003-A'
        )
        self.assertEquals(response.status_code, 200)

    def test_view_search(self):
        response = search(self.request(version=self.dated_version, q='foo'))
        self.assertEquals(response.status_code, 200)

    def test_view_search_partial(self):
        response = search_partial(self.request(
            version=self.dated_version,
            q='foo'
        ))
        self.assertEquals(response.status_code, 200)

    def test_view_sidebar_partial(self):
        response = sidebar_partial(
            self.request(),
            self.version,
            self.effective_date,
            '1003-A'
        )
        self.assertEquals(response.status_code, 200)
