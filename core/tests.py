from django.contrib.auth.models import AnonymousUser
from django.shortcuts           import reverse
from django.test                import RequestFactory, TestCase
from core.models                import Journey, User, City, Country
from template_scripts.views     import add_city_data
from mixer.backend.django       import mixer
from core.views                 import JourneyListAPIView, CityListAPIView
import pytest
import json


@pytest.mark.django_db
class ApplicantCreationTest (TestCase):
    data = {
        # "name"            : "the name",
    }
    
    def mix_journey(self, frm='ny', to='la', date='2019-01-01', postfix_date_to_name=False):
        date_postfix = ''
        if postfix_date_to_name: date_postfix = ': ' + date
        kwargs    = {
            'name'        : frm + ' to ' + to + date_postfix,
            'origin'      : getattr(self, frm, None),
            'destination' : getattr(self, to, None),
            'date'        : date,
        }
        mixer.blend(Journey, **kwargs)
    
    def setUp(self):
        self.factory = RequestFactory ()
        self.user = AnonymousUser
        request   = self.factory.get(reverse('scripts:add_city_data'))#, kwargs={"test": True}))
        response  = add_city_data(request, test=True)
        content   = json.loads(response.content)
        self.ny   = City.objects.get(name='New York')
        self.br   = City.objects.get(name='Bronx')         # close to NY
        self.ph   = City.objects.get(name='Philadelphia')  # not far from NY
        self.la   = City.objects.get(name='Los Angeles')
        self.rs   = City.objects.get(name='Riverside')     # close to LA
        
        self.pt   = City.objects.get(name='Portland')      # far from NY and LA
        self.dv   = City.objects.get(name='Denver')        # far from NY and LA
        
        self.mix_journey('ny', 'la', '2019-09-09')
        self.mix_journey('br', 'la', '2019-09-09')
        self.mix_journey('ph', 'la', '2019-09-09')
        self.mix_journey('ny', 'rs', '2019-09-08')
        self.mix_journey('rs', 'la', '2019-09-08')
        self.mix_journey('br', 'rs', '2019-09-08')
        
        self.mix_journey('pt', 'dv', '2019-08-31', postfix_date_to_name=True)
        self.mix_journey('pt', 'dv', '2019-09-02', postfix_date_to_name=True)
        self.mix_journey('pt', 'dv', '2019-09-04', postfix_date_to_name=True)
        self.mix_journey('pt', 'dv', '2019-09-05', postfix_date_to_name=True)
        self.mix_journey('pt', 'dv', '2019-09-07', postfix_date_to_name=True)
        
        self.num_of_journeys = 6 + 5
        
        # cities = sorted(cities, key=lambda a: a.distance_city(la))
        # for city in cities: print(city.id, '\t', int(city.distance_city(la)), '\t', city)
    
    # def model_request(self, model=City, **kwargs):
    #     user = kwargs.pop('user', AnonymousUser())
    #     request = self.factory.get('/api/city', kwargs)
    #     request.user = user
    #     response = CityListAPIView.as_view()(request)
    #     # response = CreateModel.as_view () (request, model_name='applicant')
    #     response.render ()
    #     return json.loads(response.content)
    
    def city_request(self, **kwargs):
        user         = kwargs.pop('user', AnonymousUser())
        request      = self.factory.get('/api/city', kwargs)
        request.user = user
        response     = CityListAPIView.as_view()(request)
        response.render()
        return json.loads(response.content)
    
    def journey_request(self, **kwargs):
        user         = kwargs.pop('user', AnonymousUser())
        request      = self.factory.get('/api/journey', kwargs)
        request.user = user
        response     = JourneyListAPIView.as_view()(request)
        response.render()
        return json.loads(response.content)

    def test_city(self):
        # Test sorting by distance
        results = self.city_request(latitude=47.6, longitude= -122.3)['results']
        assert results[0]['name'] == 'Seattle'
        r0 = results[0]
        for elem in results[1:]:
            assert elem['distance'] and elem['distance'] > r0['distance']
            r0 = elem
            
        # Test Names only
        results = self.city_request(names_only=1)['results']
        assert results[0] == {'name': 'New York'}

    def test_journey(self):
        # Test no kwargs
        response = self.journey_request()
        assert response['count'] == self.num_of_journeys

        # Test origin, destination and radius
        response = self.journey_request(origin=self.ny.id, destination=self.la.id, radius=1)
        assert response['count'] == 1
        response = self.journey_request(origin=self.ny.id, destination=self.la.id, radius=40)
        assert response['count'] == 2
        response = self.journey_request(origin=self.ny.id, destination=self.la.id, radius=120)
        assert response['count'] == 4
        response = self.journey_request(origin=self.ny.id, destination=self.la.id, radius=160)
        assert response['count'] == 5
        assert response['results'][4]['name'] == 'ph to la'
        
        # Test origin, destination and radius
        response = self.journey_request(origin=self.pt.id, destination=self.dv.id, date='2019-09-03', date_tolerance=10)
        assert response['count'] == 5
        response = self.journey_request(origin=self.pt.id, destination=self.dv.id, date='2019-09-03', date_tolerance=3)
        assert response['count'] == 4
        response = self.journey_request(origin=self.pt.id, destination=self.dv.id, date='2019-09-03', date_tolerance=2)
        assert response['count'] == 3
        response = self.journey_request(origin=self.pt.id, destination=self.dv.id, date='2019-09-03', date_tolerance=1)
        assert response['count'] == 2
        response = self.journey_request(origin=self.pt.id, destination=self.dv.id, date='2019-09-03', date_tolerance=0)
        assert response['count'] == 0
        response = self.journey_request(origin=self.pt.id, destination=self.dv.id, date='2019-09-04', date_tolerance=0)
        assert response['count'] == 1
        assert response['results'][0]['name'] == 'pt to dv: 2019-09-04'
