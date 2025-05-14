import requests
import base64
from song_class import *
# Spotify API credentials
client_id = '205f5e24e2964401bab30de9786a3147'
client_secret = '726d630e371e4888956d89d864d09ebc'

# Function to get access token
def get_access_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    }
    data = {'grant_type': 'client_credentials'}

    response = requests.post(auth_url, headers=headers, data=data)
    response_data = response.json()
    return response_data['access_token']


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def get_songs_by_genre(genre, limit=5, total_songs=200):
    # Authenticate with Spotify
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Fetch songs in batches of 50
    songs = []
    offset = 0

    while len(songs) < total_songs:
        try:
            results = sp.search(q=f'genre:{genre}', type='track', limit=50, offset=offset, market='US')

            if not results['tracks']['items']:
                break  # No more tracks available

            for track in results['tracks']['items']:
                # Get album cover (use the first available image or None)
                album_cover = track['album']['images'][0]['url'] if track['album']['images'] else None

                # Fixed the artist access (removed square brackets around 'artists')
                artists = track['artists']
                if len(artists) >= 2:
                    artist_name = f"{artists[0]['name']}, {artists[1]['name']}"
                else:
                    artist_name = artists[0]['name']

                song_obj = Song(
                    name=track['name'],
                    artist=artist_name,
                    album_cover=album_cover
                )
                song_obj = song_obj.ToString()
                songs.append(song_obj)

            offset += 50  # Move to the next batch

        except Exception as e:
            print(f"Error fetching songs: {e}")
            break

    # Shuffle and select subset
    random.shuffle(songs)
    selected_songs = songs[:limit]

    # Create dictionary with Song objects as keys
    song_dict = {song: 0 for song in selected_songs}
    return song_dict






# Function to get top 5 songs based on the input string
def search_songs(query):
    print("ASKED : " + query)
    token = get_access_token()
    search_url = 'https://api.spotify.com/v1/search'

    headers = {
        'Authorization': f'Bearer {token}'
    }

    params = {
        'q': query,
        'type': 'track',
        'limit': 3,
        'market': 'US'
    }

    response = requests.get(search_url, headers=headers, params=params)
    result = response.json()

    songs = []
    if result.get('tracks', {}).get('items'):
        for track in result['tracks']['items']:
            try:
                # Get song name
                song_name = track['name']

                # Get artists (first 2 if available)
                artists = [artist['name'] for artist in track['artists']]
                artist_str = artists[0]
                if len(artists) > 1:
                    artist_str += f", {artists[1]}"

                # Get album cover URL (highest resolution available)
                album_cover_url = ""
                if track['album']['images']:
                    album_cover_url = track['album']['images'][0]['url']  # First image is highest resolution

                # Format the string
                song_data = f"{song_name}::::{artist_str}:::::{album_cover_url}"
                songs.append(song_data)

            except Exception as e:
                print(f"Error processing track: {e}")
                continue

    return "///".join(songs) if songs else 'Nothing'
