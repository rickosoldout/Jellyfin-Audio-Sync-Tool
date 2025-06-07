import os
import time
import subprocess
from jellyfin_apiclient_python import JellyfinClient

# === CONFIGURATION ===
JELLYFIN_URL = "http://192.168.1.178:8096"
JELLYFIN_USERNAME = "im"
JELLYFIN_PASSWORD = "pokemon123"
DOWNLOAD_DIR = "/home/rickoserver/downloads"

# === CONNECT TO JELLYFIN ===
client = JellyfinClient()
client.config.data["auth.ssl"] = False

# NOTE: login() needs server_url and username
client.auth.login(
    server_url=JELLYFIN_URL,
    username=JELLYFIN_USERNAME,
    password=JELLYFIN_PASSWORD
)

# === FETCH MOVIES ===
movies = client.jellyfin.library_items(None, {'IncludeItemTypes': 'Movie'})['Items']
if not movies:
    print("❌ No movies found.")
    exit()

print("\n=== Available Movies ===")
for idx, movie in enumerate(movies):
    print(f"[{idx}] {movie['Name']} ({movie.get('ProductionYear', 'N/A')})")

choice = int(input("Select a movie: "))
selected = movies[choice]
movie_id = selected['Id']
movie_title = selected['Name']

# === GET MOVIE FILE PATH ===
movie_details = client.jellyfin.items(movie_id)
movie_path = movie_details['MediaSources'][0]['Path']
print(f"🎬 Movie file path: {movie_path}")

# === GET LANGUAGE INPUT ===
lang = input("Enter audio language (e.g., spanish, german): ").strip().lower()

# === JACKKET SEARCH + DELUGE DOWNLOAD ===
# Replace this with your working Jackett s
