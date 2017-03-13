from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from models import *
from utils import *
from api import *

import json


def regulation(request, version, eff_date, node):

    if request.method == 'GET':
        node_id = ':'.join([version, eff_date, node])
        toc_id = ':'.join([version, eff_date, 'tableOfContents'])
        meta_id = ':'.join([version, eff_date, 'preamble'])

        toc = TableOfContents.objects.get(node_id=toc_id)
        meta = Preamble.objects.get(node_id=meta_id)
        regtext = Section.objects.get(node_id=node_id)

        split_node = node.split('-')
        if len(split_node) >= 2 and split_node[1].isalpha():
            pass

        toc.get_descendants()
        meta.get_descendants(auto_infer_class=False)
        regtext.get_descendants()# (desc_type=Paragraph)

        # print regtext.str_as_tree()
        print node_id

        if regtext is not None and toc is not None:
            return render_to_response('regulation.html', {'toc': toc,
                                                          'reg': regtext,
                                                          'mode': 'reg',
                                                          'meta': meta})


def regulation_partial(request, version, eff_date, node):

    if request.method == 'GET':
        node_id = ':'.join([version, eff_date, node])
        meta_id = ':'.join([version, eff_date, 'preamble'])

        meta = Preamble.objects.get(node_id=meta_id)
        regtext = Section.objects.get(node_id=node_id)

        split_node = node.split('-')
        if len(split_node) >= 2 and split_node[1].isalpha():
            pass

        meta.get_descendants(auto_infer_class=False)
        regtext.get_descendants()

        if regtext is not None and meta is not None:
            result = render_to_string('regnode.html', {'node': regtext,
                                                       'meta': meta})
            result = '<section id="content-wrapper" class="reg-text">' + result + '</section>'
            return HttpResponse(result)
            #return render_to_response('regnode.html', {'node': regtext,
            #                                           'meta': meta})


def diff(request, left_version, left_eff_date, right_version, right_eff_date, node):

    if request.method == 'GET':
        node_id = ':'.join([left_version, left_eff_date, right_version, right_eff_date, node])
        toc_id = ':'.join([left_version, left_eff_date, right_version, right_eff_date, 'tableOfContents'])
        meta_id = ':'.join([left_version, left_eff_date, right_version, right_eff_date, 'preamble'])

        toc = TableOfContents.objects.get(node_id=toc_id)
        meta = Preamble.objects.get(node_id=meta_id)
        regtext = Section.objects.get(node_id=node_id)

        split_node = node.split('-')
        if len(split_node) >= 2 and split_node[1].isalpha():
            pass

        toc.get_descendants(desc_type=DiffNode)
        meta.get_descendants(desc_type=DiffNode)
        regtext.get_descendants(desc_type=DiffNode)

        # print regtext.str_as_tree()
        print node_id

        if regtext is not None and toc is not None:
            return render_to_response('regulation.html', {'toc': toc,
                                                          'reg': regtext,
                                                          'mode': 'diff',
                                                          'meta': meta})

def main(request):

    if request.method == 'GET':

        preamble = Preamble.objects.filter(tag='preamble')
        regs_meta = []
        for item in preamble:
            item.get_descendants()
            regs_meta.append(item)

        fdsys = RegNode.objects.filter(tag='fdsys')

        return render_to_response('main.html', {'preamble': regs_meta,
                                                'fdsys': fdsys})