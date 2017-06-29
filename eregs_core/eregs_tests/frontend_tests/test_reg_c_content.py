# -*- coding: utf-8 -*-

import unittest
from selenium import webdriver


@unittest.skip('hits production server')
class TestLandingPageRegC(unittest.TestCase):

    def setUp(self):

        self.main_url = 'https://www.consumerfinance.gov/eregulations/1003-1/2015-26607_20170101'
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1440, 900)
        self.driver.get(self.main_url)

    def test_section_1(self):

        section = self.driver.find_element_by_css_selector('section#1003-1')
        title = section.find_element_by_css_selector('h2.section-title')
        par_tree = section.find_element_by_css_selector('ol')
        par_a = par_tree.find_element_by_css_selector('li#1003-1-a')
        par_b = par_tree.find_element_by_css_selector('li#1003-1-b')
        par_c = par_tree.find_element_by_css_selector('li#1003-1-c')

        self.assertEqual(section.get_attribute('data-page-type'), 'reg-section')
        self.assertEqual(title.text.strip(), ' § 1003.1 Authority, purpose, and scope.'.decode('utf-8'))
        self.assertEqual(par_a.find_element_by_css_selector('p').text,
                         'This part, known as Regulation C, is issued by the Bureau of Consumer Financial Protection (Bureau) '
                         'pursuant to the Home Mortgage Disclosure Act (HMDA) (12 U.S.C. 2801 et seq.), as amended. '
                         'The information-collection requirements have been approved by the U.S. Office of Management '
                         'and Budget (OMB) under 44 U.S.C. 3501 et seq. and have been assigned OMB numbers for '
                         'institutions reporting data to the Office of the Comptroller of the Currency (1557-0159), '
                         'the Federal Deposit Insurance Corporation (3064-0046), the Federal Reserve System (7100-0247), '
                         'the Department of Housing and Urban Development (HUD) (2502-0529), the National Credit Union '
                         'Administration (3133-0166), and the Bureau of Consumer Financial Protection (3170-0008).')

        self.assertEqual(par_b.find_element_by_css_selector('li#1003-1-b-1 p').text,
                         'This part implements the Home Mortgage Disclosure Act, which is intended to provide the '
                         'public with loan data that can be used:')

        self.assertEqual(par_b.find_element_by_css_selector('li#1003-1-b-1-iii p').text,
                         'To assist in identifying possible discriminatory lending patterns and enforcing '
                         'antidiscrimination statutes.')

        self.assertEqual(par_b.find_element_by_css_selector('li#1003-1-b-2 p').text,
                         'Neither the act nor this part is intended to encourage unsound lending practices or the '
                         'allocation of credit.')

        self.assertEqual(par_c.find_element_by_css_selector('li#1003-1-c p').text,
                         'This part applies to certain financial institutions, including banks, savings associations, '
                         'credit unions, and other mortgage lending institutions, as defined in § 1003.2. The '
                         'regulation requires an institution to report data to the appropriate Federal agency about '
                         'home purchase loans, home improvement loans, and refinancings that it originates or '
                         'purchases, or for which it receives applications; and to disclose certain data to the public.')
