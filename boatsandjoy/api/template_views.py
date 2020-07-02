# -*- coding: UTF-8 -*-

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from boatsandjoy.boats.models import Boat
from .constants import TRANSLATIONS


@require_http_methods(['GET'])
def index(request):
    context = {'translations': TRANSLATIONS}
    return render(request, 'pages/index.html', context=context)


@require_http_methods(['GET'])
def contact(request):
    return render(request, 'pages/contact.html')


@require_http_methods(['GET'])
def points_of_interest(request):
    return render(request, 'pages/points-of-interest.html')


@require_http_methods(['GET'])
def watersports(request):
    return render(request, 'pages/watersports.html')


@require_http_methods(['GET'])
def cookies(request):
    return render(request, 'pages/cookies.html')


@require_http_methods(['GET'])
def boats(request):
    context = {'boats': Boat.objects.filter(active=True)}
    return render(request, 'pages/boats.html', context=context)
