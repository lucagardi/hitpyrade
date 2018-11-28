""" Parse HitParadeItalia page and fill a Spotify playlist """
from operator import itemgetter
import re

from six.moves import urllib
from bs4 import BeautifulSoup
from spotipy import Spotify
import spotipy.util as util

import yaml


def is_blacklisted(string, blacklisted_words):
    """ Check string against blacklisted words list (case insensitive) """
    for blacklisted_word in blacklisted_words:
        if blacklisted_word in string.lower().split():
            return True

    return False


def get_first_spotify_match(spotipy_obj, search_str, blacklisted_words=None):
    """ Return first non-blacklisted song """
    search_result = spotipy_obj.search(q=search_str, limit='10')

    # Sort by popularity
    search_result['tracks']['items'] = sorted(search_result['tracks']['items'],
                                              key=itemgetter(u'popularity'),
                                              reverse=True)

    # Discarding blaclisted words
    for track in search_result['tracks']['items']:
        if is_blacklisted(track['name'], blacklisted_words) or \
           is_blacklisted(track['album']['name'], blacklisted_words) or \
           is_blacklisted(track['artists'][0]['name'], blacklisted_words):
            print 'Discarded: %s - %s (%s)' % (track['name'],
                                               track['album']['name'],
                                               track['artists'][0]['name'])
            continue
        # Retrieve first non-blacklisted
        return track

    # No match
    return None


def hitpyrade():
    """ Retrieve page, scrape it, fill playlist in Spotify """
    # Config
    with open("hitpyrade.yml", 'r') as ymlfile:
        config = yaml.load(ymlfile)

    print config

    # Authentication
    scope = "playlist-modify-private,playlist-modify-public"
    token = util.prompt_for_user_token(config['auth']['username'],
                                       scope,
                                       config['auth']['client_id'],
                                       config['auth']['client_secret'],
                                       config['auth']['redirect_uri'])

    spotipy = Spotify(auth=token)

    # Create playlist
    sp_playlist = spotipy.user_playlist_create(config['auth']['username'],
                                               config['playlist_title'],
                                               public=False)

    # Declarative part
    playlist = []
    track_ids = []

    # Parsing
    soup = BeautifulSoup(urllib.request.urlopen(config['url']), 'html.parser')

    # Remove script tags
    for tag in soup.li('script'):
        tag.extract()

    # Replace links with their text
    for tag in soup.li('a'):
        tag.replace_with(tag.get_text())

    # Replace list elements with their text
    for tag in soup.li('li'):
        tag.replace_with(tag.get_text())

    # Clean whitespaces, accents and HitParadeItalia notes
    for song in soup.li.get_text().split('\n'):
        song = " ".join(song.split())
        song = re.sub(r"\[.*\]", '', song).strip()

        if song:
            playlist.append({"title": song})

    print 'Playlist length: %s' % len(playlist)

    # Find match in Spotify catalog
    for song in playlist:
        # Attempt search with full song name
        result = get_first_spotify_match(spotipy,
                                         song['title'],
                                         config['blacklist'])

        # Attempt search with song title
        if not result:
            result = get_first_spotify_match(spotipy,
                                             re.sub(r"\ \-.*$", '',
                                                    song['title']),
                                             config['blacklist'])

        # Give up, otherwise
        if not result:
            print "No result for %s" % song['title']

        else:
            print "Found: %s - %s (%s) P: %s" % (result['name'],
                                                 result['artists'][0]['name'],
                                                 result['album']['name'],
                                                 result['popularity'])
            # Append track ID to list
            track_ids.append(result['id'])

    print "Adding %s songs to %s" % (len(track_ids), sp_playlist['name'])

    # Add songs to playlist using track ID list
    spotipy.user_playlist_add_tracks(config['auth']['username'],
                                     sp_playlist['id'],
                                     track_ids)

    print "You're welcome!"


if __name__ == '__main__':
    hitpyrade()
