# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

# myapp/views.py
import os
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from django.conf import settings
import json

# Load dataset and train model (done only once)
csv_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'modified_shoe_market_trend_analysis.csv')
df = pd.read_csv(csv_path)

# Define features and target
X = df[['Region', 'Festival', 'Brand', 'Type', 'Material', 'Gender']]
y = df['Sales Volume']

# One-hot encode categorical variables
encoder = OneHotEncoder(sparse_output=False)
X_encoded = encoder.fit_transform(X.fillna('Unknown'))

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# Train Random Forest Regressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

def predict_trending_brand(region, festival):
    brands = df['Brand'].unique()
    brand_sales_predictions = []
    
    for brand in brands:
        new_data = pd.DataFrame({
            'Region': [region],
            'Festival': [festival],
            'Brand': [brand],
            'Type': ['Casual'],  
            'Material': ['Rubber'],  
            'Gender': ['Unisex']
        })
        new_data_encoded = encoder.transform(new_data.fillna('Unknown'))
        predicted_sales = model.predict(new_data_encoded)
        brand_sales_predictions.append((brand, predicted_sales[0]))

    ranked_brands = sorted(brand_sales_predictions, key=lambda x: x[1], reverse=True)
    top_brand = {"brand": ranked_brands[0][0], "predicted_sales": int(ranked_brands[0][1])}
    all_predictions = [{"brand": brand, "predicted_sales": int(sales)} for brand, sales in ranked_brands]

    return top_brand, all_predictions

def trending_brand_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        region = data.get('region', 'Unknown')
        festival = data.get('festival', 'Unknown')
        
        top_brand, all_predictions = predict_trending_brand(region, festival)

        return JsonResponse({
            "top_brand": top_brand,
            "all_predictions": all_predictions
        }, safe=False)
    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

def index(request):
    return render(request, 'index2.html')
