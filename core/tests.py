from django.contrib.auth.models import AnonymousUser
from django.shortcuts           import reverse
from django.test                import RequestFactory, TestCase
from core.models                import Journey, User, City, Country
from template_scripts.views     import add_city_data
import json


class ApplicantCreationTest (TestCase):
    data = {
        # "name"            : "the name",
        "email"           : "v@vacachho.com",
        "password"        : "123",
        "status"          : "hgf",
        "street"          : "st",
        "city"            : "ct",
        "zip"             : "04",
        "country"         : "de",
        "type"            : "my type",
        "contract"        : "my contract",
        "salary_range"    : [2, 4],
        "shift"           : "their shift",
        "template"        : "my template",
        "experience_years": 2,
        "start_date"      : "2019-10-28",
        "benefits"        : [1, 2],
        "fav_benefits"    : [3, 4],
        "skills"          : [{'id': 1, 'rating': 3}, {'id': 2, 'rating': 3}],
        "fav_skills"      : [1, 2],
        "phone"           : "+49432452",
        "other_contact"   : "hg",
        "homepage"        : 'https://www.google.com/h',
        "xing"            : 'https://www.google.com/x',
        "facebook"        : 'https://www.google.com/f',
        "linkedin"        : 'https://www.google.com/l',
        "video"           : 'https://www.google.com/v',
        "twitter"         : 'https://www.google.com/t'
    }
    
    def setUp(self):
        
        self.factory = RequestFactory ()
        self.user = AnonymousUser
        
        request = self.factory.get(reverse('scripts:add_city_data'))#, kwargs={"test": True}))
        response = add_city_data (request, test=True)
        # response.render ()
        content = json.loads(response.content)
        cities = City.objects.all()
        ny      = City.objects.get(name='New York')
        bronx   = City.objects.get(name='Bronx')  # close to NY
        philly  = City.objects.get(name='Philadelphia')  # not far from NY
        la      = City.objects.get(name='Los Angeles')
        rs      = City.objects.get(name='Riverside') # close to LA
        
        cities = sorted(cities, key=lambda a: a.distance_city(la))
        for city in cities: print(city.id, '\t', int(city.distance_city(la)), '\t', city)
    def test_creation(self):
        request = self.factory.post (
            reverse ('json:create_model', kwargs={"model_name": "applicant"}),
            data=json.dumps (self.data),
            content_type='application/json'
        )
        
        request.user = AnonymousUser ()
        
        response = CreateModel.as_view () (request, model_name='applicant')
        response.render ()
        content = json.loads (response.content)
        
        # test if creation returns a token
        self.assertNotEqual (content.get ('token', None), None)
        
        applicant = Applicant.objects.get (user__email=self.data.get ('email', ''))
        
        self.data['benefits'] = [{'id': 1, 'name': 'b1'}, {'id': 2, 'name': 'b2'}]
        self.data['fav_benefits'] = [{'id': 3, 'name': 'b3'}, {'id': 4, 'name': 'b4'}]
        self.data['skills'] = [{'id': 1, 'name': 's1', 'rating': None}, {'id': 2, 'name': 's2', 'rating': None}]
        self.data['fav_skills'] = [{'id': 1, 'name': 's1'}, {'id': 2, 'name': 's2'}]
        
        for key, b in self.data.items ():
            if key == 'password':
                continue
            a = getattr (applicant, key, None)
            # print(f'\n__\n\n{key}:\t\ta: {a}\t\tb: {b}')
            self.assertEqual (a, b)
        self.assertTrue (content.get ('token', ''))
