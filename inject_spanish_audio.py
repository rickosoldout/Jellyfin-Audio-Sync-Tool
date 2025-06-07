import os
import time
from jellyfin_apiclient_python import JellyfinClient
from jackett_search import search_torrents
from deluge_client import DelugeRPCClient

# === CONFIG ===
JELLYFIN_URL = "http://192.168.1.178:8096"
JELLYFIN_USER = "im"
JELLYFIN_PASSWORD = "pokemon123"

DELUGE_HOST = "127.0.0.1"
DELUGE_PORT = 58846
DELUGE_USER = "delugeuser"
DELUGE_PASS = "delugepassword"

# === MAIN MENU ===
def main():
    while True:
        print("\n=== What do you want to do? ===")
        print("[1] Search and download new media (with keywords)")
        print("[2] Inject new audio into existing Jellyfin media")
        print("[0] Quit")
        choice = input("Select an option: ")

        if choice == "1":
            search_and_download()
        elif choice == "2":
            inject_audio()
        elif choice == "0":
            break
        else:
            print("Invalid option. Try again.")

# === MODE 1: SEARCH & DOWNLOAD NEW MEDIA ===
def search_and_download():
    media_type = input("What type? (movie/show/documentary): ").strip().lower()
    title = input("Enter media title (e.g., Avatar): ").strip()
    include_keywords = input("Enter required keywords (comma separated, e.g., 2009,spanish): ").strip().lower().split(",")
    exclude_keywords = input("Enter keywords to exclude (e.g., trailer,cam): ").strip().lower().split(",")

    print(f"\n📽️ Searching for {media_type} '{title}' with keywords: {include_keywords}, excluding: {exclude_keywords}")

    # Search Jackett
    results = search_torrents(title, include_keywords, exclude_keywords)

    if not results:
        print("❌ No good results found.")
        return

    top = results[0]
    print(f"🎯 Best match: {top['title']}")
    magnet = top['magnet']

    # Send to Deluge
    try:
        client = DelugeRPCClient(DELUGE_HOST, DELUGE_PORT, DELUGE_USER, DELUGE_PASS)
        client.connect()
        client.call("core.add_torrent_magnet", magnet, {})
        print("✅ Magnet added to Deluge!")
    except Exception as e:
        print(f"❌ Deluge error: {e}")

# === MODE 2: INJECT AUDIO ===
def inject_audio():
    lang = input("Enter language keyword (e.g., spanish, latino, german): ").strip().lower()

    print(f"\n🎧 Injecting audio tracks for language: {lang} (Feature in development...)")
    # TODO: Add actual Jellyfin + ffmpeg audio injection logic here

# === JACKKET MODULE (basic example) ===
def search_torrents(title, includes, excludes):
    from urllib.parse import quote_plus
    import feedparser

    base_url = "http://localhost:9117/api/v2.0/indexers/all/results/torznab/api"
    apikey = "3vn6ers95tws1pj1ep448nhvsjqf56ac"
    query = quote_plus(title)
    url = f"{base_url}?apikey={apikey}&t=search&q={query}"

    feed = feedparser.parse(url)
    results = []

    for entry in feed.entries:
        name = entry.title.lower()
        if all(k.strip() in name for k in includes) and not any(k.strip() in name for k in excludes):
            results.append({
                "title": entry.title,
                "magnet": entry.link
            })

    return results

# === RUN ===
if __name__ == "__main__":
    main()
