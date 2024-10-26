# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]

# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('trending/', views.index, name='index2'),  # Home page view for the form
    path('trending-brand/', views.trending_brand_view, name='trending_brand'),  # API endpoint
]
