from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.conf.urls import patterns, include, url

from django.contrib import admin
from festival import settings
from tracker import views

admin.autodiscover()

dajaxice_autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.main, name='main'),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls'))
)
