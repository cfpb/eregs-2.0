import os

from django.conf import settings
from django.core.management import call_command
from django.db.models.query import QuerySet
from django.test import TestCase
from model_mommy import mommy

from eregs_core.models import Preamble, RegNode, Section


class EregsModelTests(TestCase):

    def setUp(self):
        filename = os.path.join(settings.DATA_DIR, '2011-31712.xml')
        call_command('import_xml', filename)

    def test_get_child(self):

        preamble = Preamble.objects.get(tag='preamble')
        preamble.get_descendants()
        agency = preamble.get_child('agency/regtext')
        cfr_section = preamble.get_child('cfr/section/regtext')

        self.assertEqual(
            agency.text,
            'Bureau of Consumer Financial Protection'
        )
        self.assertEqual(
            preamble.agency,
            'Bureau of Consumer Financial Protection'
        )
        self.assertEqual(cfr_section.text, '1003')

    def test_get_children(self):

        section = Section.objects.get(node_id='2011-31712:2011-12-30:1003-1')
        section.get_descendants()
        paragraphs = section.paragraphs
        self.assertEqual(paragraphs[0].label, '1003-1-a')


class TestRegNodeQuerySet(TestCase):
    def test_filter_by_attribs_returns_queryset(self):
        mommy.make(RegNode, attribs={'foo': 'bar'})
        self.assertIsInstance(
            RegNode.objects.filter_by_attribs(foo='bar'),
            QuerySet
        )

    def test_filter_by_attribs_returns_correct_match(self):
        mommy.make(RegNode, _quantity=10, attribs={'something': 'else'})
        node = mommy.make(RegNode, attribs={'foo': 'bar'})
        self.assertEquals(
            RegNode.objects.filter_by_attribs(foo='bar').get(),
            node
        )

    def test_filter_by_attribs_doesnt_match_the_wrong_thing(self):
        mommy.make(RegNode, _quantity=10, attribs={'something': 'else'})
        self.assertFalse(RegNode.objects.filter_by_attribs(foo='bar').exists())

    def test_filter_by_attribs_matches_null(self):
        node = mommy.make(RegNode, attribs={'foo': None})
        self.assertEquals(
            RegNode.objects.filter_by_attribs(foo=None).get(),
            node
        )

    def test_filter_by_attribs_doesnt_match_nested(self):
        mommy.make(RegNode, attribs={'something': {'foo': 'bar'}})
        self.assertFalse(RegNode.objects.filter_by_attribs(foo='bar').exists())

    def test_filter_by_attribs_doesnt_match_nested_null(self):
        mommy.make(RegNode, attribs={'something': {'foo': None}})
        self.assertFalse(RegNode.objects.filter_by_attribs(foo=None).exists())

    def test_filter_by_attribs_strings_dont_match(self):
        mommy.make(RegNode, attribs='{"foo":"bar"}')
        self.assertFalse(RegNode.objects.filter_by_attribs(foo='bar').exists())

    def test_filter_by_attribs_matches_non_strings(self):
        node = mommy.make(RegNode, attribs={'foo': 123})
        self.assertEquals(
            RegNode.objects.filter_by_attribs(foo=123).get(),
            node
        )
