from django.test import TestCase
from django.core.management import call_command
from eregs_core.models import *

# Create your tests here.


class EregsModelTests(TestCase):

    def setUp(self):

        filename = '/Users/vinokurovy/Development/regulations-xml/regulation/1003/2011-31712.xml'
        call_command('import_xml', filename)

    def test_get_child(self):

        preamble = Preamble.objects.get(tag='preamble')
        preamble.get_descendants()
        agency = preamble.get_child('agency/regtext')
        cfr_section = preamble.get_child('cfr/section/regtext')

        self.assertEqual(agency.text, 'Bureau of Consumer Financial Protection')
        self.assertEqual(preamble.agency, 'Bureau of Consumer Financial Protection')
        self.assertEqual(cfr_section.text, '1003')

    def test_get_children(self):

        section = Section.objects.get(node_id='2011-31712:2011-12-30:1003-1')
        section.get_descendants()
        paragraphs = section.paragraphs
        self.assertEqual(paragraphs[0].label, '1003-1-a')