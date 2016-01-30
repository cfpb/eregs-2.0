from django.shortcuts import render, render_to_response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from models import *
from utils import get_with_descendants, regtext

import json


def regulation(request, version, eff_date, node):

    if request.method == 'POST':
        print version
        json_data = json.loads(request.body)

        return render(request, 'main.html')

    elif request.method == 'GET':
        # print version
        # return render(request, 'main.html')
        node_id = ':'.join([version, eff_date, node])
        data = get_with_descendants(regtext, node_id)
        if data is not None:
            return JsonResponse(data)
        else:
            return JsonResponse({})


def main(request):

    print 'testing'

    if request.method == 'GET':
        return render_to_response('main.html')