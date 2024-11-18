import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize Spotipy with client credentials
client_id = '205f5e24e2964401bab30de9786a3147'        # Replace with your Spotify Client ID
client_secret = '726d630e371e4888956d89d864d09ebc' # Replace with your Spotify Client Secret

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Function to search for a song and get its Spotify URL
def get_song_url(song_name):
    results = sp.search(q=song_name, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        song_url = track['external_urls']['spotify']
        song_name = track['name']
        artist_name = track['artists'][0]['name']
        print(f"Song: {song_name} by {artist_name}")
        print(f"Spotify URL: {song_url}")
        return song_url
    else:
        print("No results found for this song.")
        return None


# Example usage
song = input("Enter song`s name: ")
get_song_url(song)
