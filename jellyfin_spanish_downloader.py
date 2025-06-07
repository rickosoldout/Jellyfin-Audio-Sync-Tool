import requests
import re

SPANISH_KEYWORDS = [
    "dual audio", "español", "latino", "castellano", "esp", "spa", "spanish"
]

def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower()).strip()

def score_torrent(torrent, jellyfin_title, jellyfin_year):
    title = normalize(torrent["Title"])
    jtitle = normalize(jellyfin_title)

    score = 0
    if jtitle in title:
        score += 40
    elif all(word in title for word in jtitle.split()):
        score += 30

    if str(jellyfin_year) in title:
        score += 20

    if any(kw in title for kw in SPANISH_KEYWORDS):
        score += 30

    if "2160p" in title or "4k" in title:
        score += 15
    elif "1080p" in title:
        score += 10

    try:
        score += int(torrent.get("Seeders", 0)) // 10
    except:
        pass

    return score

def search_torrents_auto(jackett_api_url, jackett_api_key, query, jellyfin_title, jellyfin_year):
    print(f"🔍 Searching Jackett for '{query}' with Spanish audio keywords...")

    params = {
        "apikey": jackett_api_key,
        "Query": query,
        "Category[]": "2000"  # Movies category
    }

    response = requests.get(jackett_api_url, params=params)

    try:
        results = response.json()["Results"]
    except Exception as e:
        print("❌ Failed to decode JSON from Jackett. Response was:")
        print(response.text)
        return None

    if not results:
        print("❌ No torrents found.")
        return None

    scored = sorted(
        results,
        key=lambda x: score_torrent(x, jellyfin_title, jellyfin_year),
        reverse=True
    )

    best_match = scored[0]
    print(f"✅ Auto-selected: {best_match['Title']}")
    return best_match

def send_to_deluge(magnet_uri):
    # Placeholder function - replace with your Deluge RPC code
    print(f"Sending to Deluge: {magnet_uri}")
    # Implement Deluge sending here

def main():
    # Replace these with your actual values
    JACKETT_API_URL = "http://localhost:9117/api/v2.0/indexers/all/results"
    JACKETT_API_KEY = "YOUR_JACKETT_API_KEY"
    selected_title = "Avatar"
    selected_year = 2009

    best_match = search_torrents_auto(
        jackett_api_url=JACKETT_API_URL,
        jackett_api_key=JACKETT_API_KEY,
        query=selected_title,
        jellyfin_title=selected_title,
        jellyfin_year=selected_year
    )

    if best_match:
        send_to_deluge(best_match["MagnetUri"])
        print("✔️ Magnet sent to Deluge!")
    else:
        print("⚠️ No suitable torrent found.")

if __name__ == "__main__":
    main()
