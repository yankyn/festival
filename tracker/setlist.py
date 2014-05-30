__author__ = 'Nathaniel'

import requests
from bs4 import BeautifulSoup
import pyfoobar
import re


def sanitize_artist(artist):
    return artist.replace('?', '')


def get_artist_id(artist_name):
    base_url = 'http://www.setlist.fm/search?query=%s'
    url_name = '+'.join(sanitize_artist(artist_name).split(' '))
    url = base_url % url_name
    response = requests.get(url)
    if not response.ok:
        raise Exception()
    page = response.content
    soup = BeautifulSoup(page)
    a = soup.find('a', {'title': 'Show only setlists by %s' % artist_name})
    return a.get('href').split('=')[-1]


def get_artist_year_page(artist, year):
    artist_id = get_artist_id(artist)
    artist = sanitize_artist(artist)
    base_url = 'http://www.setlist.fm/stats/%s-%s.html?year=%d'
    artist_name = '-'.join(map(lambda x: x.lower(), artist.split(' ')))
    url = base_url % (artist_name, artist_id, year)
    response = requests.get(url)
    if not response.ok:
        raise Exception()
    page = response.content
    return BeautifulSoup(page)


def find_play_count(soup, year):
    import datetime

    count_list = soup.find('div', {'class': 'artistplayCounts'})
    years = count_list.findChildren('li')
    for year_tag in years:
        year_a = year_tag.findChildren('a')[0]
        year_span = year_a.findChild('span')
        if str(year_span.string) == str(year):
            count_a = year_tag.findChildren('a')[1]
            count_span = count_a.findChild('span')
            if count_span.text.isdigit():
                return int(count_span.text)
    return 0


def find_song(year_page, name):
    results = year_page.findAll('tr', {'class': 'songRow'})
    for result in results:
        name_tag = result.find('a', {'class': 'songName'})
        if name_tag and name_tag.text.lower() in name.lower() or name_tag.text.lower().replace(' ',
                                                                                               '') in name.lower().replace(
                ' ', ''):
            number_tag = result.find('td', {'class': "songCount"})
            inner = number_tag.findChildren('span')[-1]
            if inner.text.isdigit():
                return int(inner.text)
    return 0


def percentile_by_artist_and_song(artist, song, min_count=10):
    import datetime

    current_year = datetime.datetime.now().year
    generic_year_page = get_artist_year_page(artist, current_year)
    years = {}
    total_count = 0
    year = current_year
    while total_count < min_count:
        count = find_play_count(generic_year_page, year)
        total_count += count
        years[year] = count
        year -= 1
    plays = 0
    year_song_plays = {}
    for year in years:
        song_plays = find_song(get_artist_year_page(artist, year), song)
        if song_plays is not None:
            year_song_plays[year] = song_plays
            plays += song_plays
    return years, year_song_plays


def analyze_playing_track(artist, track):
    show_years, play_years = percentile_by_artist_and_song(artist, track)

    years = {}
    for year in show_years:
        years[year] = (show_years[year], play_years.get(year))
        # artist, track, percentage, years(plays, shows)
    return years


def get_playing_track(foobar):
    artist = foobar.getCurrentArtist().title()
    track = foobar.getCurrentTrack().title().replace(' Of ', ' of ').replace(' The ', ' the ').replace('?', '')
    if re.match('[0-9]+ - .*', track):
        track = re.sub('[0-9]+ - ', '', track)
    return artist, track