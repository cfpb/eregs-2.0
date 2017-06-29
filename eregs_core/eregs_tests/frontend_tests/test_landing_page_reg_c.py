# -*- coding: utf-8 -*-

import unittest
from selenium import webdriver


@unittest.skip('hits production server')
class TestLandingPageRegC(unittest.TestCase):

    def setUp(self):

        self.main_url = 'http://www.consumerfinance.gov/eregulations/1003'
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1440, 900)
        self.driver.get(self.main_url)

    def test_header(self):

        header = self.driver.find_element_by_tag_name('header')
        main_head = header.find_element_by_class_name('main-head')
        title = main_head.find_element_by_class_name('site-title')
        eregs_link = main_head.find_element_by_xpath('div/h1/a')
        reg_title = main_head.find_element_by_xpath('div/h2/a')
        nav = main_head.find_element_by_xpath('nav')
        navlist = nav.find_element_by_tag_name('ul')
        nav_list_items = navlist.find_elements_by_css_selector('.app-nav-list-item')

        self.assertEqual(eregs_link.text, 'eRegulations')
        self.assertEqual(reg_title.text, '12 CFR Part 1003 (Regulation C)')

        self.assertEqual(nav_list_items[0].text, 'Regulations')
        self.assertEqual(nav_list_items[1].text, 'About')
        self.assertEqual(nav_list_items[2].find_element_by_xpath('a/img').get_attribute('class'), 'logo')
        self.assertEqual(nav_list_items[2].find_element_by_xpath('a/img').get_attribute('alt'),
                         'Consumer Financial Protection Bureau')

    def test_subheader(self):

        subheader = self.driver.find_element_by_css_selector('header div.sub-head div.toc-head')
        drawer_links = subheader.find_elements_by_css_selector('ul.drawer-toggles li a')
        eff_date = self.driver.find_element_by_css_selector('header div.sub-head div#content-header span.effective-date')

        self.assertEqual(drawer_links[0].get_attribute('id'), 'menu-link')
        self.assertEqual(drawer_links[1].get_attribute('id'), 'timeline-link')
        self.assertEqual(drawer_links[2].get_attribute('id'), 'search-link')
        self.assertEqual(eff_date.text, 'Effective Date: 1/1/2017')

    def test_table_of_contents(self):

        toc = self.driver.find_element_by_id('menu')
        toc_drawer = toc.find_element_by_css_selector('div.drawer-header')

        self.assertEqual(toc_drawer.text, 'TABLE OF CONTENTS')

        nav_toc = toc.find_element_by_css_selector('nav#toc')
        toc_links = nav_toc.find_elements_by_css_selector('ol li a')

        self.assertEqual(toc_links[0].text, '§ 1003.1\nAuthority, purpose, and scope.'.decode('utf-8'))
        self.assertEqual(toc_links[0].get_attribute('data-section-id'), '1003-1')
        self.assertEqual(toc_links[1].text, '§ 1003.2\nDefinitions.'.decode('utf-8'))
        self.assertEqual(toc_links[1].get_attribute('data-section-id'), '1003-2')
        self.assertEqual(toc_links[2].text, '§ 1003.3\nExempt institutions.'.decode('utf-8'))
        self.assertEqual(toc_links[2].get_attribute('data-section-id'), '1003-3')
        self.assertEqual(toc_links[3].text, '§ 1003.4\nCompilation of loan data.'.decode('utf-8'))
        self.assertEqual(toc_links[3].get_attribute('data-section-id'), '1003-4')
        self.assertEqual(toc_links[4].text, '§ 1003.5\nDisclosure and reporting.'.decode('utf-8'))
        self.assertEqual(toc_links[4].get_attribute('data-section-id'), '1003-5')
        self.assertEqual(toc_links[5].text, '§ 1003.6\nEnforcement.'.decode('utf-8'))
        self.assertEqual(toc_links[5].get_attribute('data-section-id'), '1003-6')
        self.assertEqual(toc_links[6].text, 'Appendix A to Part 1003\nForm and Instructions for Completion of HMDA Loan/Application Register')
        self.assertEqual(toc_links[6].get_attribute('data-section-id'), '1003-A')
        self.assertEqual(toc_links[7].text, 'Appendix B to Part 1003\nForm and Instructions for Data Collection on Ethnicity, Race, and Sex')
        self.assertEqual(toc_links[7].get_attribute('data-section-id'), '1003-B')
        self.assertEqual(toc_links[8].text, 'INTERPRETATIONS\nIntroduction')
        self.assertEqual(toc_links[8].get_attribute('data-section-id'), '1003-Interp-h1')
        self.assertEqual(toc_links[9].text, 'INTERPRETATIONS FOR\nRegulation Text')
        self.assertEqual(toc_links[9].get_attribute('data-section-id'), '1003-Subpart-Interp')
        self.assertEqual(len(toc_links), 10)

        headings = nav_toc.find_elements_by_css_selector('ol li h3')

        self.assertEqual(headings[0].text, 'APPENDICES')
        self.assertEqual(headings[1].text, 'SUPPLEMENT I TO PART 1003 - Staff Commentary')
        self.assertEqual(len(headings), 2)

    def test_landing_main(self):

        section = self.driver.find_element_by_css_selector('section.landing')
        banner = section.find_element_by_css_selector('h2.banner-text')

        self.assertEqual(section.get_attribute('data-page-type'), 'landing-page')
        self.assertEqual(section.get_attribute('data-reg-part'), '1003')
        self.assertEqual(banner.text, 'Regulation C requires many financial institutions to collect, report, '
                                      'and disclose information about their mortgage lending activity.')

        alert = section.find_element_by_css_selector('div.alert')

        self.assertEqual(alert.find_element_by_css_selector('div.alert_effective-date').text,
                         'New amendments effective: 01/01/2018')
        self.assertEqual(alert.find_element_by_css_selector('div.alert_view-link').text,
                         'View amended regulation')

        group = section.find_element_by_css_selector('div.group')
        col1 = section.find_elements_by_css_selector('div.group div.reg-tags')[0]
        col2 = section.find_elements_by_css_selector('div.group div.reg-tags')[1]

        self.assertEqual(col1.find_element_by_css_selector('h3.list-header').text.strip(),
                         'Financial institutions include:')
        self.assertEqual(col2.find_element_by_css_selector('h3.list-header').text.strip(),
                         'The regulation covers topics such as:')

        instituions = col1.find_elements_by_css_selector('ul li')
        topics = col2.find_elements_by_css_selector('ul li')

        self.assertEqual(instituions[0].text, 'Banks')
        self.assertEqual(instituions[1].text, 'Savings associations')
        self.assertEqual(instituions[2].text, 'Credit unions')
        self.assertEqual(instituions[3].text, 'Mortgage lenders')

        self.assertEqual(topics[0].text, 'Data compilation')
        self.assertEqual(topics[1].text, 'Reporting and disclosure')
        self.assertEqual(topics[2].text, 'Recordkeeping')
        self.assertEqual(topics[3].text, 'Mortgage')

        landing_link = section.find_element_by_css_selector('div p.landing-curent-link')
        contact_info = section.find_element_by_css_selector('div.well')

        self.assertEqual(landing_link.text, 'View the currently effective Regulation C')
        self.assertEqual(contact_info.find_element_by_css_selector('h4.sentence-header').text,
                         'We want to hear from you!')
        self.assertEqual(contact_info.find_elements_by_css_selector('p')[0].text,
                         'Please take our survey to help the Bureau decide whether to expand and maintain eRegulations.')
        self.assertEqual(contact_info.find_elements_by_css_selector('p')[1].text,
                         'For questions or comments about the platform:')
        self.assertEqual(contact_info.find_element_by_css_selector('ul li address').text,
                         'CFPB_eRegs_team@cfpb.gov')
