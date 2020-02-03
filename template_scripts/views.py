import json
import os
import csv
from django.http            import HttpResponse
from core.models            import City, Country, User, Journey
from django.core.exceptions import MultipleObjectsReturned
from django.views.decorators.http import require_POST
from mixer.backend.django   import mixer
from random import randint
import datetime
# import names
from core.models import STATIC_CITIES


def add_city_data(request, test=False):
    data_path = os.path.join('backend', 'template_scripts', 'data', 'worldcities.csv')
    population_limit = 50_000
    if test:
        population_limit = 500_000
    data_path = os.path.join ('C:\\Users\\Hussam\\Desktop\\appdev_project', data_path)
    with open (data_path, mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if row["population"] and float(row["population"]) > population_limit:
                if test and row["iso2"] != 'US': continue
                if not test and row["iso2"] not in ['DE',  'ES', 'FR', 'GB', 'NL',]: continue
                cntry, crtd = Country.objects.get_or_create(name__iexact=row["country"])
                
                if crtd:
                    cntry.name  = row["country"]
                    cntry.iso   = row["iso2"]
                    cntry.save()
                try:
                    city,  crtd = City.objects.get_or_create(name__iexact=row["city_ascii"], country=cntry)
                
                    if crtd:
                        city.name       = row["city_ascii"]
                        city.population = int(float(row["population"]))
                        city.latitude   = row["lat"]
                        city.longitude  = row["lng"]
                        city.save()
                except MultipleObjectsReturned:
                    pass
                    # print('ERROR TWO CITIES:', row["city_ascii"])
                

                city.save()
    return HttpResponse(json.dumps("done!"), content_type="application/json")

FM = [0, 1, 1, 0, 0, 1, 1, 0, 0, 0]
CLOSE_CITIES = ['Dresden', 'Leipzig', 'Berlin']

@require_POST
def add_journeys(request):
    data_path = os.path.join('backend', 'template_scripts', 'data', 'csv_journeys.csv')
    data_path = os.path.join('C:\\Users\\Hussam\\Desktop\\appdev_project', data_path)
    with open(data_path, mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            bid = randint(3, 12)
            try:
                user = User.objects.get(id=bid)
            except:
                user = User(id=bid)
                gender = 'male'
                if FM[bid-3] == 0: gender='female'
                # fn = names.get_first_name(gender=gender)
                # ln = names.get_last_name()
                # user.first_name = fn
                # user.last_name  = ln
                # user.email      = f'{fn}.{ln}.{bid}@example.com'
                # user.username   = f'{fn}{bid}'
                user.save()
            # origin_idx = randint(0, len(STATIC_CITIES) - 1)
            origin_idx = randint(0, len(CLOSE_CITIES) - 1)
            destin_idx = origin_idx
            while destin_idx == origin_idx: destin_idx = randint(0, len(STATIC_CITIES)-1)
            org = City.objects.get(name=CLOSE_CITIES[origin_idx])
            dst = City.objects.get(name=STATIC_CITIES[destin_idx]['name'])
            kwargs = {
            'origin'            : org,
            'destination'       : dst,
            'date'              : datetime.date.today() + datetime.timedelta(days=randint(-10, 13)),# row['date'],
            # '_phone'            : row['phone'],
            'description'       : row['description'],
            'available_weight'  : row['available_weight'],
            'user'              : user,
            }
            journey = Journey(**kwargs)
            journey.save()
    return HttpResponse(json.dumps("done!"), content_type="application/json")
