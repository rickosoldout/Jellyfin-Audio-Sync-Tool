import requests

# === CONFIG ===
base_url = "http://192.168.1.178:8096"
api_key = "521425dc932b42e3a07b87dc0c80628b"  # Replace with your actual API key

headers = {
    "X-Emby-Token": api_key,
    "Accept": "application/json"
}

try:
    print("🔐 Connecting to Jellyfin...")

    # Get movies
    resp = requests.get(f"{base_url}/Items", headers=headers, params={
        'IncludeItemTypes': 'Movie',
        'Recursive': 'true',
        'Limit': 200  # Adjust if needed
    })
    resp.raise_for_status()
    movies = resp.json()['Items']

    print(f"🎬 Found {len(movies)} movies:")
    for idx, movie in enumerate(movies):
        name = movie['Name']
        year = movie.get('ProductionYear', 'N/A')
        print(f"[{idx}] {name} ({year})")

except requests.HTTPError as e:
    print("❌ HTTP error:", e)
    print("Response:", e.response.text)
except Exception as e:
    print("❌ General error:", e)
