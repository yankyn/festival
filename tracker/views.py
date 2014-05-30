import datetime
import json
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import loader, RequestContext
import pyfoobar
from tracker.setlist import analyze_playing_track, get_playing_track
from tracker.models import Track, TrackYear
from django.utils import timezone


def get_percent(years):
    total_shows = 0
    total_plays = 0
    for year in years:
        shows, plays = years.get(year)
        total_shows += shows
        total_plays += plays
    if total_shows:
        return float(total_plays) * 100 / total_shows
    else:
        return 0.0


def get_last_track():
    if Track.objects.all():
        last_track = Track.objects.order_by('-last_played')[0]
        return last_track
    return None


def get_track(artist, track_name):
    track = None
    analyze_track = False
    if Track.objects.all():
        last_track = Track.objects.order_by('-last_played')[0]
        analyze_track = False
        if last_track.artist == artist and last_track.track == track_name:
            track = last_track
    if not track:
        tracks = Track.objects.filter(artist=artist, track=track_name)
        if tracks:
            track = tracks[0]
            now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
            if track.last_played - now > datetime.timedelta(days=30):
                analyze_track = True
        else:
            track = Track(artist=artist, track=track_name)
            analyze_track = True
    return track, analyze_track


def create_years(years, track):
    for year in years:
        track_year = TrackYear(track=track, year=year, shows=years.get(year)[0], plays=years.get(year)[1])
        track_year.save()


class Year(object):
    def __init__(self, year, shows, plays):
        self.year = year
        self.shows = shows
        self.plays = plays


class OtherTrack(object):
    def __init__(self, artist, track, percent, time):
        self.artist = artist
        self.track = track
        self.percent = percent
        self.time = time


def main(request):
    foobar = pyfoobar.foobar()
    artist, track_name = get_playing_track(foobar)
    track, analyze_track = get_track(artist, track_name)
    track.last_played = datetime.datetime.now()
    track.save()

    if analyze_track:
        years = analyze_playing_track(artist, track_name)
        create_years(years, track)
    else:
        years = track.get_years()

    percent = str(get_percent(years))[:4]

    year_objects = []
    for year in years:
        year_object = Year(year=year, shows=years.get(year)[0], plays=years.get(year)[1])
        year_objects.append(year_object)

    other_tracks = []
    for other_track in Track.objects.order_by('-last_played')[1:10]:
        other_tracks.append(
            OtherTrack(artist=other_track.artist, track=other_track.track,
                       percent=str(get_percent(other_track.get_years()))[:4],
                       time=other_track.last_played))

    template = loader.get_template('tracker/base.html')
    context = RequestContext(request, {
        'percent': percent,
        'track': track,
        'years': year_objects,
        'other_tracks': other_tracks
    })
    del foobar
    return HttpResponse(template.render(context))