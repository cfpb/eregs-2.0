from unittest import TestCase


class UrlPatternsTestCase(TestCase):
    def test_urlpatterns_import_succeeds(self):
        from eregs_core.urls import urlpatterns
        self.assertTrue(urlpatterns)
