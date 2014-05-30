from django.db import models


class Track(models.Model):
    artist = models.CharField(max_length=200)
    track = models.CharField(max_length=200)
    last_played = models.DateTimeField('date played')

    def title(self):
        return '%s - %s' % (self.artist, self.track)

    def get_years(self):
        years = {}
        for year in TrackYear.objects.filter(track=self):
            years[year.year] = (year.shows, year.plays)
        return years


class TrackYear(models.Model):
    shows = models.IntegerField()
    year = models.IntegerField()
    plays = models.IntegerField()
    track = models.ForeignKey(Track)