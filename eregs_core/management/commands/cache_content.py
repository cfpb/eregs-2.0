from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from eregs_core.models import *
from eregs_core.utils import xml_to_json
from lxml import etree
from itertools import product, chain

import os
import json
import requests


class Command(BaseCommand):

    help = 'Cache the views of the specified regulation.'

    def add_arguments(self, parser):
        parser.add_argument('regs', nargs='*', type=str)

    def handle(self, *args, **options):
        regs_to_cache = options['regs']
        preambles = Preamble.objects.filter(tag='preamble').exclude(reg_version__version=None)
        base = 'http://localhost:8000'
        section_tags = ['section', 'interpSection', 'appendixSection']

        versions = []

        for pre in preambles:
            pre.get_descendants()
            if pre.cfr_section in regs_to_cache:
                document_number = pre.document_number
                effective_date = pre.effective_date
                versions.append(document_number + ':' + effective_date)
                version = Version.objects.get(version=document_number + ':' + effective_date)
                sections = RegNode.objects.filter(reg_version=version, tag__in=section_tags)
                section_urls = [base + '/regulation/{}/{}/{}'.format(document_number, effective_date, section.label)
                                for section in sections if section.label.strip() != '']
                for url in section_urls:
                    r = requests.get(url)
                    print 'cached {}, result: {}'.format(r.url, r.status_code)

        diff_preambles = Preamble.objects.filter(tag='preamble',
                                                 reg_version__version=None,
                                                 left_version__in=versions,
                                                 right_version__in=versions)

        for pre in diff_preambles:
            pre.get_descendants()
            if pre.cfr_section in regs_to_cache:
                version = pre.version
                sections = RegNode.objects.filter(reg_version=version, tag__in=section_tags)
                section_urls = [base + '/diff/{}/{}/{}/{}/{}'.format(version.left_doc_number,
                                                                     version.left_eff_date,
                                                                     version.right_doc_number,
                                                                     version.right_eff_date,
                                                                     section.label) for section in sections]
                for url in section_urls:
                    r = requests.get(url)
                    print 'cached {}, result: {}'.format(r.url, r.status_code)
