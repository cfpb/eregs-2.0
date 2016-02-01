from django.shortcuts import render, render_to_response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from models import *
from utils import *
from api import *

import json


def regulation(request, version, eff_date, node):

    if request.method == 'GET':
        # print version
        # return render(request, 'main.html')
        node_id = ':'.join([version, eff_date, node])
        toc_id = ':'.join([version, eff_date, 'tableOfContents'])
        data = get_with_descendants(regtext, node_id)
        toc_data = toc.find_one({'node_id': toc_id})

        if data is not None and toc_data is not None:
            return render_to_response('regulation.html', {'toc': toc_data,
                                                          'reg': data})

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


def main(request):

    if request.method == 'GET':
        preamble = meta_api(meta_tag='preamble')
        fdsys = meta_api(meta_tag='fdsys')
        return render_to_response('main.html', {'preamble': preamble,
                                                'fdsys': fdsys})