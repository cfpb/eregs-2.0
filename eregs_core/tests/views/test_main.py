import os

from django.conf import settings
from django.core.management import call_command
from django.test import RequestFactory, TestCase

from eregs_core.views.main import MainView


class TestMainView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = MainView.as_view()

    def test_view_renders_without_any_data(self):
        request = self.factory.get('/')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    def test_post_to_view_returns_method_not_allowed(self):
        request = self.factory.post('/')
        response = self.view(request)
        self.assertEqual(response.status_code, 405)

    def test_view_renders_with_data(self):
        filename = os.path.join(settings.DATA_DIR, 'header-only.xml')
        call_command('import_xml', filename)

        request = self.factory.get('/')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Regulation TEST')
