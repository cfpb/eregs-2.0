# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from eregs_core.models import *


class ModelFunctionsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ModelFunctionsTest, cls).setUpClass()
        for fn in ('2011-31712.xml', '2015-26607_20180101.xml'):
            call_command('import_xml', os.path.join(settings.DATA_DIR, fn))

    def test_get_descendants(self):

        preamble = Preamble.objects.get(
            tag='preamble',
            reg_version__version='2011-31712:2011-12-30'
        )

        preamble.get_descendants()
        agency = preamble.get_child('agency/regtext')
        cfr_section = preamble.get_child('cfr/section/regtext')

        self.assertEqual(agency.text, 'Bureau of Consumer Financial Protection')
        self.assertEqual(preamble.agency, 'Bureau of Consumer Financial Protection')
        self.assertEqual(cfr_section.text, '1003')

        section = Section.objects.get(node_id='2011-31712:2011-12-30:1003-1')
        section.get_descendants()
        paragraphs = section.paragraphs

        self.assertEqual(paragraphs[0].label, '1003-1-a')

    def test_get_ancestors(self):

        paragraph = Paragraph.objects.get(node_id='2011-31712:2011-12-30:1003-1-a')
        ancestors = list(paragraph.get_ancestors())

        section = ancestors[-2]
        reg = ancestors[0]

        self.assertEqual(section.node_id, '2011-31712:2011-12-30:1003-1')
        self.assertEqual(section.tag, 'section')
        self.assertEqual(reg.version, '2011-31712:2011-12-30')
        self.assertEqual(reg.tag, 'regulation')
        self.assertEqual(reg.left, 1)

    def test_get_interpretations(self):

        paragraph = Paragraph.objects.get(node_id='2011-31712:2011-12-30:1003-4-a-1')
        interps = list(paragraph.get_interpretations())

        self.assertEqual(interps[0].paragraph_title, 'Paragraph 4(a)(1).')
        self.assertEqual(interps[0].label, '1003-4-a-1-Interp')
        self.assertEqual(interps[0].interp_target(), '4(a)(1)')

    def test_get_analysis(self):

        paragraph = Paragraph.objects.get(node_id='2015-26607:2018-01-01:1003-1-c')
        analyses = paragraph.get_analysis()

        a_section = analyses[0]

        self.assertEqual(a_section.target(), '1003-1-c')
        self.assertEqual(a_section.effective_date(), '2018-01-01')

        # print a_section.effective_date(), a_section.section_title()

        section = Section.objects.get(node_id='2015-26607:2018-01-01:1003-2')
        analyses = section.get_all_analyses()

        self.assertEqual(analyses[0].target(), '1003-2-a')
        self.assertEqual(analyses[-1].target(), '1003-2-q')

    def test_regnode_functions(self):

        section = RegNode.objects.get(node_id='2015-26607:2018-01-01:1003-2')
        markerless_par = RegNode.objects.get(node_id='2015-26607:2018-01-01:1003-2-p1')
        markerless_par.get_descendants(auto_infer_class=True)
        markerless_subpar = markerless_par.children[0]
        marked_par1 = markerless_par.children[1]
        marked_par2 = markerless_par.children[2]

        self.assertEqual(markerless_par.marker_type, '')
        self.assertEqual(marked_par1.marker_type, 'a')
        self.assertEqual(markerless_par.inner_list_type(), 'a')
        self.assertEqual(section.inner_list_type(), 'none')
        self.assertEqual(marked_par1.inner_list_type(), 'none')
        self.assertEqual(marked_par2.inner_list_type(), '1')
        self.assertEqual(marked_par1.node_url(), '/regulation/2015-26607/2018-01-01/1003-2#1003-2-a')

    def test_preamble_functions(self):

        preamble = Preamble.objects.get(node_id='2011-31712:2011-12-30:preamble')
        preamble.get_descendants(auto_infer_class=False)

        self.assertEqual(preamble.agency, 'Bureau of Consumer Financial Protection')
        self.assertEqual(preamble.reg_letter, 'C')
        self.assertEqual(preamble.cfr_title, '12')
        self.assertEqual(preamble.cfr_section, '1003')
        self.assertEqual(preamble.effective_date, '2011-12-30')
        self.assertEqual(preamble.document_number, '2011-31712')
        self.assertEqual(preamble.cfr_url, 'https://www.federalregister.gov/articles/2011/12/19/2011-31712/home-mortgage-disclosure-regulation-c')
        self.assertEqual(preamble.reg_url, '/regulation/2011-31712/2011-12-30/1003-1')

    def test_fdsys_functions(self):

        fdsys = Fdsys.objects.get(node_id='2011-31712:2011-12-30:fdsys')
        fdsys.get_descendants(auto_infer_class=False)

        self.assertEqual(fdsys.cfr_title, '12')
        self.assertEqual(fdsys.cfr_title_text, 'Banks and Banking')
        self.assertEqual(fdsys.date, '2011-12-19')
        self.assertEqual(fdsys.part_title, 'HOME MORTGAGE DISCLOSURE')
        self.assertEqual(fdsys.volume, '8')
        self.assertEqual(fdsys.original_date, '2012-01-01')

    def test_toc_functions(self):

        toc = TableOfContents.objects.get(node_id='2011-31712:2011-12-30:tableOfContents')
        toc.get_descendants(auto_infer_class=True)

        self.assertEqual(len(toc.section_entries), 6)
        self.assertEqual(len(toc.appendix_entries), 2)
        self.assertEqual(len(toc.interp_entries), 2)
        self.assertEqual(toc.has_appendices, True)
        self.assertEqual(toc.has_interps, True)
        #self.assertEqual(toc.supplement_title.decode('utf-8'), 'Supplement I to part 1003-Staff Commentary')

        toc_entry = toc.section_entries[0]

        self.assertEqual(toc_entry.target(), '1003-1')
        self.assertEqual(toc_entry.section_number, '1')
        self.assertEqual(toc_entry.section_subject, ' Authority, purpose, and scope.')

        app_entry = toc.appendix_entries[0]

        self.assertEqual(app_entry.target(), '1003-A')
        self.assertEqual(app_entry.appendix_letter, 'A')
        #self.assertEqual(app_entry.appendix_subject, 'Appendix A to Part 1003&#8212;Form and Instructions for Completion of HMDA Loan/Application Register')

        interp_entry = toc.interp_entries[0]

        self.assertEqual(interp_entry.target(), '1003-Interp-h1')
        self.assertEqual(interp_entry.interp_title, 'Introduction')

    def test_section_functions(self):

        section = Section.objects.get(node_id='2011-31712:2011-12-30:1003-1')
        section.get_descendants()

        self.assertEqual(section.section_number(), '1')
        self.assertEqual(section.label, '1003-1')
        #self.assertEqual(section.subject, '&#167; 1003.1 Authority, purpose, and scope.')

    def test_paragraph_functions(self):

        par = Paragraph.objects.get(node_id='2011-31712:2011-12-30:1003-1-a')
        par.get_descendants()
        content_nodes = par.paragraph_content
        marked_up_content = """This part, known as Regulation C, is issued by the Bureau of Consumer Financial Protection (Bureau) pursuant to the Home Mortgage Disclosure Act (HMDA) (<a href="USC:12-2801" class="citation definition" data-definition="USC:12-2801" data-defined-term="12 U.S.C. 2801" data-gtm-ignore="true">12 U.S.C. 2801</a> et seq.), as amended. The information-collection requirements have been approved by the U.S. Office of Management and Budget (OMB) under <a href="USC:44-3501" class="citation definition" data-definition="USC:44-3501" data-defined-term="44 U.S.C. 3501" data-gtm-ignore="true">44 U.S.C. 3501</a> et seq. and have been assigned OMB numbers for institutions reporting data to the Office of the Comptroller of the Currency (1557-0159), the Federal Deposit Insurance Corporation (3064-0046), the Federal Reserve System (7100-0247), the Department of Housing and Urban Development (HUD) (2502-0529), the National Credit Union Administration (3133-0166), and the Bureau of Consumer Financial Protection (3170-0008)."""

        self.assertIsNone(par.target())
        self.assertIsNone(par.interp_target())
        self.assertEquals(par.formatted_label(), '1003.1(a)')
        self.assertTrue(par.has_content)
        self.assertFalse(par.has_diff_content)
        self.assertEquals(len(content_nodes), 5)
        self.assertEquals(par.marked_up_content(), marked_up_content)

    def test_ref_and_def_functions(self):

        par = Paragraph.objects.get(node_id='2015-26607:2018-01-01:1003-2-e')
        par.get_descendants()
        content_nodes = par.paragraph_content

        self.assertEquals(len(content_nodes), 8)

        defn = content_nodes[0]
        term_ref = content_nodes[2]
        internal_ref = content_nodes[6]

        self.assertEqual(defn.term(), 'covered loan')
        self.assertEqual(defn.regtext(), 'Covered loan')
        self.assertEqual(term_ref.reftype(), 'term')
        self.assertEqual(term_ref.target(), '1003-2-d')
        self.assertEqual(term_ref.regtext(), 'closed-end mortgage loan')
        self.assertEqual(term_ref.target_url(), '/regulation/2015-26607/2018-01-01/1003-2#1003-2-d')

        self.assertEqual(internal_ref.reftype(), 'internal')
        self.assertEqual(internal_ref.target(), '1003-3-c')
        self.assertEqual(internal_ref.regtext(), '1003.3(c)')
        self.assertEqual(internal_ref.target_url(), '/regulation/2015-26607/2018-01-01/1003-3#1003-3-c')

