import json
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from django.http import HttpResponse
import pyfoobar
from tracker.setlist import get_playing_track
from tracker.views import get_last_track

__author__ = 'Nathaniel'


@dajaxice_register
def skip_song(request):
    foobar = pyfoobar.foobar()
    foobar.next()
    dajax = Dajax()
    return dajax.json()


@dajaxice_register
def check_refresh(request):
    foobar = pyfoobar.foobar()
    artist, track_name = get_playing_track(foobar)
    last_track = get_last_track()
    if artist != last_track.artist or track_name != last_track.track:
        response = {'success': True}
    else:
        response = {'success': False}
    return HttpResponse(json.dumps(response), content_type="application/json")