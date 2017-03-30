from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from models import *
from utils import *
from api import *

import json
import time

from dateutil import parser as dt_parser


def regulation(request, version, eff_date, node):

    if request.method == 'GET':
        node_id = ':'.join([version, eff_date, node])
        toc_id = ':'.join([version, eff_date, 'tableOfContents'])
        meta_id = ':'.join([version, eff_date, 'preamble'])

        toc = TableOfContents.objects.get(node_id=toc_id)
        meta = Preamble.objects.get(node_id=meta_id)
        regtext = Section.objects.get(node_id=node_id)

        toc.get_descendants()
        meta.get_descendants(auto_infer_class=False)
        regtext.get_descendants()

        regulations = [r for r in RegNode.objects.filter(label=meta.cfr_section) if len(r.version.split(':')) == 2]
        regulations = sorted(regulations, key=lambda x: x.version.split(':')[1], reverse=True)
        timeline = []

        for reg in regulations:
            preamble = Preamble.objects.filter(node_id=reg.version + ':preamble').order_by('version')
            fdsys = Fdsys.objects.filter(node_id=reg.version + ':fdsys').order_by('version')
            for pre, fd in zip(preamble, fdsys):
                pre.get_descendants(auto_infer_class=False)
                fd.get_descendants(auto_infer_class=False)
                timeline.append((pre, fd))


        #timeline = [preamble for reg in regulations
        #            for preamble in Preamble.objects.filter(node_id=reg.version + ':preamble')]

        #for t in timeline:
        #    t.get_descendants(auto_infer_class=False)

        #print [t.effective_date for t in timeline]

        if regtext is not None and toc is not None:
            return render_to_response('regulation.html', {'toc': toc,
                                                          'reg': regtext,
                                                          'mode': 'reg',
                                                          'meta': meta,
                                                          'timeline': timeline})


def regulation_partial(request, version, eff_date, node):

    if request.method == 'GET':
        node_id = ':'.join([version, eff_date, node])
        meta_id = ':'.join([version, eff_date, 'preamble'])

        t0 = time.time()

        meta = Preamble.objects.get(node_id=meta_id)
        regtext = Section.objects.get(node_id=node_id)

        meta.get_descendants(auto_infer_class=False)
        regtext.get_descendants()
        t1 = time.time()
        print 'Database query took {}'.format(t1 - t0)

        if regtext is not None and meta is not None:
            t2 = time.time()
            result = render_to_string('regnode.html', {'node': regtext,
                                                       'mode': 'reg',
                                                       'meta': meta})
            result = '<section id="content-wrapper" class="reg-text">' + result + '</section>'
            t3 = time.time()
            print 'Template rendering took {}'.format(t3 - t2)
            return HttpResponse(result)


def sidebar_partial(request, version, eff_date, node):

    if request.method == 'GET':
        node_id = ':'.join([version, eff_date, node])
        meta_id = ':'.join([version, eff_date, 'preamble'])

        meta = Preamble.objects.get(node_id=meta_id)
        regtext = Section.objects.get(node_id=node_id)

        meta.get_descendants(auto_infer_class=False)
        regtext.get_descendants()

        if regtext is not None:
            return render_to_response('right_sidebar.html', {'node': regtext,
                                                             'mode': 'reg',
                                                             'meta': meta})

def definition_partial(request, version, eff_date, node):

    if request.method == 'GET':
        node_id = ':'.join([version, eff_date, node])
        regtext = Paragraph.objects.get(node_id=node_id)
        regtext.get_descendants()

        if regtext is not None:
            return render_to_response('definition.html', {'node': regtext,
                                                          'mode': 'reg'})


def sxs_partial(request, version, eff_date, node):

    if request.method == 'GET':
        node_id = ':'.join([version, eff_date, node])
        meta_id = ':'.join([version, eff_date, 'preamble'])

        meta = Preamble.objects.get(node_id=meta_id)
        regtext = Section.objects.get(node_id=node_id)

        meta.get_descendants(auto_infer_class=False)
        regtext.get_analysis()

        footnotes = [elem for child in regtext.analysis[0].children if child.tag == 'analysisParagraph'
                     for elem in child.children if elem.tag == 'footnote']

        if regtext is not None:
            return render_to_response('sxs.html', {'node': regtext,
                                                   'footnotes': footnotes,
                                                   'mode': 'reg'})


def diff_redirect(request, left_version, left_eff_date):

    if request.method == 'GET':
        new_version = request.GET['new_version'].split(':')
        print left_version, left_eff_date
        sections = Section.objects.filter(version=left_version + ':' + left_eff_date,
                                          tag='section').exclude(label='').order_by('label')
        first_section = sections[0]
        print first_section
        return HttpResponseRedirect('/diff/{}/{}/{}/{}/{}'.format(
            left_version, left_eff_date, new_version[0], new_version[1], first_section.label
        ))


def diff(request, left_version, left_eff_date, right_version, right_eff_date, node):

    if request.method == 'GET':
        node_id = ':'.join([left_version, left_eff_date, right_version, right_eff_date, node])
        toc_id = ':'.join([left_version, left_eff_date, right_version, right_eff_date, 'tableOfContents'])
        meta_id = ':'.join([left_version, left_eff_date, right_version, right_eff_date, 'preamble'])

        toc = DiffNode.objects.get(node_id=toc_id)
        meta = DiffNode.objects.get(node_id=meta_id)
        regtext = DiffNode.objects.get(node_id=node_id)

        toc.get_descendants(desc_type=DiffNode)
        meta.get_descendants(desc_type=DiffNode)
        regtext.get_descendants(desc_type=DiffNode)

        toc.__class__ = TableOfContents
        meta.__class__ = DiffPreamble
        regtext.__class__ = Section

        if regtext is not None and toc is not None:
            return render_to_response('regulation.html', {'toc': toc,
                                                          'reg': regtext,
                                                          'mode': 'diff',
                                                          'meta': meta})


def regulation_main(request, part_number):

    if request.method == 'GET':

        regulations = [r for r in RegNode.objects.filter(label=part_number) if len(r.version.split(':')) == 2]
        regulations = sorted(regulations, key=lambda x: x.version.split(':')[1], reverse=True)

        most_recent_reg = regulations[0]
        toc_id = most_recent_reg.version + ':tableOfContents'
        meta_id = most_recent_reg.version + ':preamble'

        toc = TableOfContents.objects.get(node_id=toc_id)
        meta = Preamble.objects.get(node_id=meta_id)

        toc.get_descendants()
        meta.get_descendants(auto_infer_class=False)

        landing_page = 'landing_pages/reg_{}.html'.format(meta.cfr_section)
        landing_page_sidebar = 'landing_pages/reg_{}_sidebar.html'.format(meta.cfr_section)

        if toc is not None and meta is not None:
            return render_to_response('regulation.html', {'toc': toc,
                                                          'meta': meta,
                                                          'mode': 'landing',
                                                          'landing_page': landing_page,
                                                          'landing_page_sidebar': landing_page_sidebar})


def main(request):

    if request.method == 'GET':

        # meta = Preamble.objects.filter(tag='preamble')
        meta = [r for r in Preamble.objects.filter(tag='preamble') if len(r.version.split(':')) == 2]
        meta = sorted(meta, key=lambda x: x.version.split(':')[1], reverse=True)

        regs_meta = []
        reg_parts = set()

        for item in meta:
            item.get_descendants(auto_infer_class=False)
            if item.reg_letter not in reg_parts:
                regs_meta.append(item)
                reg_parts.add(item.reg_letter)

        fdsys = RegNode.objects.filter(tag='fdsys')

        return render_to_response('main.html', {'preamble': regs_meta,
                                                'fdsys': fdsys})
