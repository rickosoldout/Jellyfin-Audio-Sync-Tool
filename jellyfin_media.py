import requests

JELLYFIN_URL = "http://localhost:8096"
API_KEY = "521425dc932b42e3a07b87dc0c80628b"  # 🔁 Replace with your real key

def get_jellyfin_movies():
    url = f"{JELLYFIN_URL}/Users/me/Items"
    headers = {
        "X-Emby-Token": API_KEY
    }
    params = {
        "IncludeItemTypes": "Movie",
        "Recursive": "true"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("Items", [])

def get_media_file_path(item_id):
    url = f"{JELLYFIN_URL}/Items/{item_id}"
    headers = {
        "X-Emby-Token": API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("MediaSources", [{}])[0].get("Path")
    return None
