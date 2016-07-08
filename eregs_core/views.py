from django.shortcuts import render, render_to_response
from django.http import JsonResponse
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

        toc.get_descendants(desc_type=ToCEntry)
        meta.get_descendants()
        regtext.get_descendants(desc_type=Paragraph)

        # print regtext.str_as_tree()

        if regtext is not None and toc is not None:
            return render_to_response('regulation.html', {'toc': toc,
                                                          'reg': regtext,
                                                          'meta': meta})


def regulation_partial(request, version, eff_date, node):

    if request.method == 'GET':
        if 'Interp' in node:
            coll = interps
        else:
            coll = regtext
        node_id = ':'.join([version, eff_date, node])
        data = get_with_descendants(coll, node_id)
        metadata = meta_api(version, eff_date)

        if data is not None and metadata is not None:
            return render_to_response('regnode.html', {'node': data,
                                                       'meta': metadata})


def interpretations(request, version, eff_date, node):

    if request.method == 'GET':
        # print version
        # return render(request, 'main.html')
        node_id = ':'.join([version, eff_date, node])
        toc_id = ':'.join([version, eff_date, 'tableOfContents'])
        data = get_with_descendants(interps, node_id)
        metadata = meta_api(version, eff_date)
        toc_data = get_with_descendants(toc, toc_id)
            #toc.find_one({'node_id': toc_id})

        if data is not None and toc_data is not None:
            return render_to_response('regulation.html', {'toc': toc_data,
                                                          'reg': data,
                                                          'meta': metadata})

def regulation_json(request, version, eff_date, node):

    if request.method == 'GET':
        # print version
        # return render(request, 'main.html')
        node_id = ':'.join([version, eff_date, node])
        data = get_with_descendants(regtext, node_id)
        if data is not None:
            return JsonResponse(data)
        else:
            return JsonResponse({})


def meta_json(request, version=None, eff_date=None):

    if request.method == 'GET':

        data = meta_api(version, eff_date)

        if data is not None:
            return JsonResponse(data)
        else:
            return JsonResponse({})


def toc_json(request, version, eff_date):
    if request.method == 'GET':
        data = toc_api(version, eff_date)
        return JsonResponse(data)

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