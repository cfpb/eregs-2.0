import os

from django.test import TestCase
from django.core.management import call_command

from eregs.local_settings import REGML_ROOT
from eregs_core.models import RegNode, Preamble, Section


class DataLoadTests(TestCase):

    def setUp(self):

        self.xml_file = os.path.join(REGML_ROOT, 'regulation', '1003', '2011-31712.xml')
        call_command('import_xml', self.xml_file)

    def test_import_file(self):

        root = RegNode.objects.get(tag='regulation', reg_version__version='2011-31712:2011-12-30')

        self.assertEqual(root.tag, 'regulation')
        self.assertEqual(root.version, '2011-31712:2011-12-30')
        self.assertEqual(root.left, 1)
