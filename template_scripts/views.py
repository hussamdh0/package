import json
import os
import csv
from django.http            import HttpResponse
from core.models            import City, Country
from django.core.exceptions import MultipleObjectsReturned

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
