from django.contrib import admin
from django.urls import path
from django.conf.urls import include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('scripts/', include ('template_scripts.urls', namespace="scripts")),

]

