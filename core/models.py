from django.contrib.auth.models import AbstractUser, UserManager
from django.db                  import models
from math                       import pi, sqrt, sin, cos, atan2
from datetime                   import date, timedelta, datetime
from django.core.exceptions     import PermissionDenied
from django.utils.translation   import gettext_lazy as _
from django.utils               import timezone
# from django.db.models         import Q


# mixin


class HasContact(models.Model):
    class Meta:
        abstract = True
    
    _phone = models.CharField(max_length=30, db_column='phone', blank=True, null=True)
    _email = models.CharField(max_length=30, db_column='cemail', blank=True, null=True)


class HasLocation(models.Model):
    class Meta:
        abstract = True
    
    latitude    = models.FloatField(unique=False, null=True, blank=True)
    longitude   = models.FloatField(unique=False, null=True, blank=True)

    # returns distance between two sets of coordinates in KM
    def distance(self, longitude=0, latitude=0, o=None):
        if o:
            if o == self:
                return 0
            latitude  = o.latitude
            longitude = o.longitude
        latitude1  = latitude
        longitude1 = longitude
        latitude2  = self.latitude
        longitude2 = self.longitude
        if all((latitude1, longitude1, latitude2, longitude2)):
            dtor = float (pi / 180.0)
    
            d_latitude  = (latitude2  - latitude1)  * dtor
            d_longitude = (longitude2 - longitude1) * dtor
    
            a = pow( sin( d_latitude/2), 2) + cos( latitude1*dtor) * cos( latitude2*dtor) * pow( sin( d_longitude/2), 2)
            c = 2 * atan2( sqrt( a), sqrt( 1-a))
            return 6367 * c
        return 1000
    
    def distance_object(self, o):
        return self.distance(longitude=o.longitude, latitude=o.latitude)


# abstract


class BaseModel(models.Model):
    objects         = models.Manager()
    name            = models.CharField(max_length=255, unique=False, null=True, blank=True)
    creation_date   = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    last_modified   = models.DateTimeField(auto_now=True, blank=False, null=True, editable=False)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        abstract = True


class BaseUserModel(AbstractUser):
    def __str__(self):
        return str(self.username)

    class Meta:
        abstract = True
        

# models and managers

class Country(models.Model):
    name = models.CharField(max_length=64, unique=True,  null=True, blank=True)
    iso  = models.CharField(max_length=2,  unique=False, null=True, blank=True)
    
    def __str__(self):
        return str(self.name)


class CityManager(models.Manager):
    def all_ordered(self, **kwargs):
        if 'search' in kwargs:
            kw = kwargs['search']
            lkw = len(kw)
            qs = self.filter(name__icontains=kw).order_by('-population')
            if lkw < 3:
                return qs
            return sorted(qs, key=lambda a: a.name.lower()[0:lkw] != kw.lower())
            
        qs = self.get_queryset()
        if 'longitude' in kwargs and 'latitude' in kwargs:
            return sorted(qs, key=lambda a: a.distance(**kwargs))
        if 'longitude' in kwargs:
            qs = qs.filter(longitude__gt=kwargs['longitude'] - 3, longitude__lt=kwargs['longitude'] + 3)
        if 'latitude' in kwargs:
            qs = qs.filter(latitude__gt=kwargs['latitude'] - 3, latitude__lt=kwargs['latitude'] + 3)
        return qs.order_by('-population')
    
    def get_json(self, value):
        if type(value) is int:
            return self.get(id=value)
        if type(value) is str:
            qs = self.filter(name__iexact=value)
            res = None
            if len(qs) == 1:
                res = qs[0]
            if len(qs) > 1:
                res = qs[0]
                for e in qs[1:]:
                    if e.population > res.population:
                        res = e
            return res
        
        
class City(HasLocation):
    name        = models.CharField(max_length=64, unique=True, null=True, blank=True)
    country     = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='city')
    population  = models.IntegerField(unique=False, null=True, blank=True)
    objects     = CityManager()
    
    def __str__(self):
        return str(self.name)


# class CUserManager(UserManager):
#     def create(self, username=None, password=None):
#         # username = kwargs.pop('email', '')
#         # password = kwargs.pop('password', '')
#
#         if not username:
#             raise ValueError("Username must be provided to create user")
#
#         user = self.model(username=username)
#         # if created:
#         #     user.username = username
#         if password:
#             # set password if provided
#             user.set_password(password)
#         user.save()
#         return user


class User(BaseUserModel, HasContact, HasLocation):
    objects     = UserManager()
    avatar      = models.CharField(max_length=1024, null=True, blank=True)
    email       = models.EmailField(_('email address'), blank=False, null=False, unique=True)
    reset_token = models.CharField(max_length=16, blank=True, null=True, default=None)
    
    @property
    def successful_journeys(self):
        return Journey.objects.filter(user=self, date__lt=date.today(), successful=True).count()
    
    @property
    def full_name(self):
        res = self.get_full_name()
        if res is not None and res != '': return res
        return self.username
    
    @full_name.setter
    def full_name(self, value):
        if type(value) is str:
            value_split = value.split(' ')
            if len(value_split) == 2:
                self.first_name = value_split[0]
                self.last_name = value_split[1]
            else:
                self.first_name = value
        else: raise TypeError
    
    # def save(self, *args, **kwargs):
    #     if not self.username:
    #         self.username = self.email
    #     if not self.email:
    #         self.email = self.username
    #     super(User, self).save(*args, **kwargs)


class JourneyManager(models.Manager):
    @staticmethod
    def filter_date(qs, **kwargs):
        d = kwargs['date']  # date
        t = timedelta(days=kwargs['date_tolerance'])  # number of tolerance days
        min, max = (d-t, d+t)
        return [x for x in qs if x.date >= min and x.date <= max]

    @staticmethod
    def filter_city(qs, city_id, s='origin', radius=0):
        d = 3
        try: city_id = int(city_id)
        except: pass
        city = City.objects.get_json(city_id)
        if radius:
            return [x for x in qs if getattr(x, s, None).distance(longitude=city.longitude, latitude=city.latitude) < radius], city
        else:
            kwargs = {
                f'{s}__longitude__gt': city.longitude - d, f'{s}__longitude__lt': city.longitude + d,
                f'{s}__latitude__gt' : city.latitude  - d, f'{s}__latitude__lt':  city.latitude  + d
            }
            return qs.filter(**kwargs), city
    
    def all_ordered(self, **kwargs):
        d = None # date
        u = kwargs.get('user', None)
        init_filter_kwargs = {}
        init_filter_args = []
        if 'my_journeys' in kwargs: init_filter_kwargs['user'] = u
        else: init_filter_args.append( ~models.Q(user=u) )
        if kwargs['recent']: init_filter_kwargs['last_modified__gt'] = datetime.now(tz=timezone.utc) - timedelta(minutes=10)
        if 'date' in kwargs:
            d = kwargs['date']  # date
            t = timedelta(days=kwargs['date_tolerance'])  # number of tolerance days
            today = date.today()
            date_range = [max(today, d - t), max(today, d + t)]
            init_filter_kwargs['date__range']=date_range

        qs = self.filter(*init_filter_args, **init_filter_kwargs)
        radius = kwargs.pop('radius', 50)
        c1 = None
        c2 = None
        # if 'date' in kwargs:          qs = self.filter_date(qs, **kwargs)
        if 'origin' in kwargs:        qs, c1 = self.filter_city(qs, kwargs['origin'],         s='origin',       radius=radius)
        if 'destination' in kwargs:   qs, c2 = self.filter_city(qs, kwargs['destination'],    s='destination',  radius=radius)
        date_key  = lambda a: abs(a.date - d)
        dist_key  = lambda a: a.origin.distance(o=c1) + a.destination.distance(o=c2)
        udist_key = lambda a: a.user.distance(o=u)
        if d and c1 and c2: key=lambda a: (date_key(a), dist_key(a))
        elif c1 and c2:     key=lambda a:  dist_key(a)
        elif d and u:       key=lambda a: (date_key(a), udist_key(a))
        elif d:             key=lambda a:  date_key(a)
        elif u:             key=lambda a:  udist_key(a)
        else:               key=lambda a: 1
        qs = sorted(qs, key=key)  # lambda a: a.origin.distance(o=c1) + a.destination.distance(o=c2))
        return qs
    
    # def create(self, name=None, origin=None, destination=None, user=None, date=None):
    def create(self, **kwargs):
        if kwargs['user'] is None or kwargs['user'].is_anonymous:
            raise PermissionDenied('Please log in to add a journey.')
        journey_obj = self.model()
        for kwarg in kwargs:
            setattr(journey_obj, kwarg, kwargs[kwarg])
        journey_obj.save()
        return journey_obj


class Journey(BaseModel, HasContact):
    name             = models.CharField(max_length=255, unique=False, null=True, blank=True)
    description      = models.CharField(max_length=255, null=True, blank=True)
    available_weight = models.IntegerField(default=1)
    origin           = models.ForeignKey(City, on_delete=models.CASCADE, related_name='journey_origin')
    destination      = models.ForeignKey(City, on_delete=models.CASCADE, related_name='journey_destination')
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journey')
    date             = models.DateField(default=date.today)
    time             = models.TimeField(null=True)
    successful       = models.BooleanField(default=False)
    objects          = JourneyManager()

    @property
    def _destination(self):
        return str(self.destination)
        
    @_destination.setter
    def _destination(self, value):
        self.destination = City.objects.get_json(value)

    @property
    def _origin(self):
        return  str(self.origin)

    @_origin.setter
    def _origin(self, value):
        self.origin = City.objects.get_json(value)
    
    
    @property
    def phone(self):
        if self._phone: return self._phone
        return self.user._phone
    
    @phone.setter
    def phone(self, value):
        self._phone = value
        
    @property
    def email(self):
        if self._email: return self._email
        return self.user.email
    
    @email.setter
    def email(self, value):
        self._email = value

    
    def __str__(self):
        return f'{str(self.name)}: from {str(self.origin)} to {str(self.destination)}'

