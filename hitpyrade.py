""" Parse HitParadeItalia page and fill a Spotify playlist

Spotify result example:

{u'album':
    {u'album_type': u'album',
     u'name': u'Identikit',
     u'external_urls': {u'spotify': u'https://open.spotify.com/album/0n2a67pM7sw2eCQO8ZCP2k'},
     u'release_date': u'2013-11-19',
     u'uri': u'spotify:album:0n2a67pM7sw2eCQO8ZCP2k',
     u'total_tracks': 20,
     u'href': u'https://api.spotify.com/v1/albums/0n2a67pM7sw2eCQO8ZCP2k',
     u'artists': [{u'name': u'Piero Pel\xf9',
                   u'external_urls': {u'spotify': u'https://open.spotify.com/artist/6gTrPTTb3XgiLt7GGcmf8j'},
                    u'uri': u'spotify:artist:6gTrPTTb3XgiLt7GGcmf8j',
                    u'href': u'https://api.spotify.com/v1/artists/6gTrPTTb3XgiLt7GGcmf8j',
                    u'type': u'artist', u'id': u'6gTrPTTb3XgiLt7GGcmf8j'}],
     u'images': [{u'url': u'https://i.scdn.co/image/0def2ca5f34ea702c8f484178a9711657327474b', u'width': 640, u'height': 640},
                 {u'url': u'https://i.scdn.co/image/793aadd4f298bc65d376831201bbd7e2ab23da99', u'width': 300, u'height': 300},
                 {u'url': u'https://i.scdn.co/image/dab42ea43b30f42d486edd84f30c07d3cc43d875', u'width': 64, u'height': 64}],
     u'type': u'album',
     u'id': u'0n2a67pM7sw2eCQO8ZCP2k',
     u'available_markets': [u'AD', u'AE', u'AR', u'AT', u'AU', u'BE', u'BG', u'BH', u'BO', u'BR', u'CA', u'CH', u'CL', u'CO', u'CR', u'CY',
                            u'CZ', u'DE', u'DK', u'DO', u'DZ', u'EC', u'EE', u'EG', u'ES', u'FI', u'FR', u'GB', u'GR', u'GT', u'HK', u'HN',
                            u'HU', u'ID', u'IE', u'IL', u'IS', u'IT', u'JO', u'JP', u'KW', u'LB', u'LI', u'LT', u'LU', u'LV', u'MA', u'MC',
                            u'MT', u'MX', u'MY', u'NI', u'NL', u'NO', u'NZ', u'OM', u'PA', u'PE', u'PH', u'PL', u'PS', u'PT', u'PY', u'QA',
                            u'RO', u'SA', u'SE', u'SG', u'SK', u'SV', u'TH', u'TN', u'TR', u'TW', u'US', u'UY', u'VN', u'ZA'],
     u'release_date_precision': u'day'},
    u'is_local': False,
    u'name': u'Il mio nome \xe8 mai pi\xf9 - Version 2008',
    u'uri': u'spotify:track:0cRDweVNsNm0KfFSxvrOf7',
    u'external_urls': {u'spotify': u'https://open.spotify.com/track/0cRDweVNsNm0KfFSxvrOf7'},
    u'popularity': 17,
    u'explicit': False,
    u'preview_url': u'https://p.scdn.co/mp3-preview/23189108d6fb211c42d94063a409e0b0001ad6ac?cid=04fd542d026c43f4b7870578548652c6',
    u'track_number': 19,
    u'disc_number': 1,
    u'href': u'https://api.spotify.com/v1/tracks/0cRDweVNsNm0KfFSxvrOf7',
    u'artists': [{u'name': u'Piero Pel\xf9',
                  u'external_urls': {u'spotify': u'https://open.spotify.com/artist/6gTrPTTb3XgiLt7GGcmf8j'},
                  u'uri': u'spotify:artist:6gTrPTTb3XgiLt7GGcmf8j',
                  u'href': u'https://api.spotify.com/v1/artists/6gTrPTTb3XgiLt7GGcmf8j',
                  u'type': u'artist',
                  u'id': u'6gTrPTTb3XgiLt7GGcmf8j'}],
    u'duration_ms': 288026,
    u'external_ids': {u'isrc': u'ITB511301690'},
    u'type': u'track',
    u'id': u'0cRDweVNsNm0KfFSxvrOf7',
    u'available_markets': [u'AD', u'AE', u'AR', u'AT', u'AU', u'BE', u'BG', u'BH', u'BO', u'BR', u'CA', u'CH', u'CL', u'CO',
                           u'CR', u'CY', u'CZ', u'DE', u'DK', u'DO', u'DZ', u'EC', u'EE', u'EG', u'ES', u'FI', u'FR', u'GB',
                           u'GR', u'GT', u'HK', u'HN', u'HU', u'ID', u'IE', u'IL', u'IS', u'IT', u'JO', u'JP', u'KW', u'LB',
                           u'LI', u'LT', u'LU', u'LV', u'MA', u'MC', u'MT', u'MX', u'MY', u'NI', u'NL', u'NO', u'NZ', u'OM',
                           u'PA', u'PE', u'PH', u'PL', u'PS', u'PT', u'PY', u'QA', u'RO', u'SA', u'SE', u'SG', u'SK', u'SV',
                           u'TH', u'TN', u'TR', u'TW', u'US', u'UY', u'VN', u'ZA
"""

from six.moves import urllib
from bs4 import BeautifulSoup, Comment
from spotipy import Spotify
import spotipy.util as util

from spotipy.oauth2 import SpotifyClientCredentials
import re
import sys
import unidecode
from collections import OrderedDict
from operator import attrgetter, itemgetter

def is_blacklisted(string):
    """ Check string against blacklisted words list (case insensitive) """
    for blacklisted_word in blacklisted_words:
        if blacklisted_word in string.lower().split():
            return True

    return False

def get_first_song(search_str):
    """ Return first non-blacklisted song """
    result = spotify.search(q=search_str, limit='10')

    # Sort by popularity
    result['tracks']['items'] = sorted(result['tracks']['items'], key=itemgetter(u'popularity'), reverse=True)

    # Discarding blaclisted words
    for track in result['tracks']['items']:
        blacklisted = False
        if is_blacklisted(track['name']) or \
           is_blacklisted(track['album']['name']) or \
           is_blacklisted(track['artists'][0]['name']):
               print 'Discarded: %s - %s (%s)' % (track['name'],
                                                  track['album']['name'],
                                                  track['artists'][0]['name'])
               continue

        return track
    else:
        return None

# Blacklisted words
blacklisted_words = [u'karaoke',
                     u'remix',
                     u'originally',
                     u'instrumental',
                     u'tribute']

# Scraping and playlist config
url = "http://www.hitparadeitalia.it/hp_yends/hpe2001.htm"
playlist_title = "Hit Parade Italia - Italy's 2001"

# Authentication config
# TODO: move to config file
username = "<SPOTIFY-USERNAME>"
client_id = "<SPOTIFY-CLIENT-ID>"
client_secret = "<SPOTIFY-CLIENT-SECRET>"
redirect_uri = "<REDIRECT-URI>"

# Authentication
scope = "playlist-modify-private,playlist-modify-public"
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
creds = SpotifyClientCredentials(client_id=client_id,
                                 client_secret=client_secret)
spotify = Spotify(auth=token)

# Create playlist
sp_playlist = spotify.user_playlist_create(username, playlist_title, public=False)
print sp_playlist

# Declarative part
playlist = []
track_ids = []

# Parsing
html_doc = urllib.request.urlopen(url)
soup = BeautifulSoup(html_doc, 'html.parser')

# Remove script tags
for script_tag in soup.li('script'):
    script_tag.extract()

# Replace links with their text
for s in soup.li('a'):
    s.replace_with(s.get_text())

# Replace list elements with their text
for s in soup.li('li'):
    s.replace_with(s.get_text())

# Clean whitespaces, accents and HitParadeItalia notes
for song in soup.li.get_text().split('\n'):
    song = " ".join(song.split())
    song = re.sub(r"\[.*\]", '', song).strip()

    if song is not '':
        playlist.append({"title": song})

print 'Playlist length: %s' % len(playlist)

# Find match in Spotify catalog
for song in playlist:
    # Attempt search with full song name
    search_result = get_first_song(song['title'])

    # Attempt search with song title
    if not search_result:
        search_result = get_first_song(re.sub(r"\ \-.*$", '', song['title']))

    # Give up, otherwise
    if not search_result:
        print "No result for %s" % song['title']

    else:
        print "Found: %s - %s (%s) POP: %s" % (search_result['name'],
                                       search_result['artists'][0]['name'],
                                       search_result['album']['name'],
                                       search_result['popularity'])
        # Append track ID to list
        track_ids.append(search_result['id'])

print "Adding %s songs to %s" % (len(track_ids), sp_playlist['name'])

# Add songs to playlist using track ID list
spotify.user_playlist_add_tracks(username, sp_playlist['id'], track_ids)

print "You're welcome!"
