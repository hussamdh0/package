from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import include



urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('scripts/',    include ('template_scripts.urls', namespace="scripts")),
    path('api/',        include ('core.urls',             namespace="api")),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
