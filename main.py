import os
import time
import shutil
import subprocess
import requests
import json

# CONFIG
JELLYFIN_URL = "http://192.168.1.178:8096"
JELLYFIN_API_TOKEN = "521425dc932b42e3a07b87dc0c80628b"
JACKETT_API_KEY = "3vn6ers95tws1pj1ep448nhvsjqf56ac"
JACKETT_URL = "http://localhost:9117/api/v2.0/indexers/all/results"
DELUGE_URL = "http://localhost:8112/json"
DELUGE_PASSWORD = "deluge"
DELUGE_DOWNLOAD_FOLDER = "/path/to/deluge/downloads"

# Expanded language keywords for better torrent searching
LANGUAGE_KEYWORDS = {
    "ENG": ["english", "eng"],
    "SPA": ["spanish", "español", "castellano", "spa", "esp"],
    "LAT": ["latin", "lat"],
    "GER": ["german", "deutsch", "deu", "ger"],
    "FRA": ["french", "français", "fra", "fr"],
    "ARA": ["arabic", "ara", "arab"],
    "JPN": ["japanese", "jpn", "jp"],
    "CMN": ["mandarin", "cmn", "chinese", "zh"],
    "ITA": ["italian", "ita", "it"],
}

def get_language_keywords(code):
    code = code.strip().upper()
    return LANGUAGE_KEYWORDS.get(code, [code.lower()])

def add_torrent(magnet_link):
    session = requests.Session()
    login_payload = {"method": "auth.login", "params": [DELUGE_PASSWORD], "id": 1}
    r = session.post(DELUGE_URL, json=login_payload)
    if not r.json().get("result", False):
        print("❌ Deluge login failed.")
        return False
    add_payload = {"method": "core.add_torrent_magnet", "params": [magnet_link, {}], "id": 2}
    r = session.post(DELUGE_URL, json=add_payload)
    if r.json().get("error"):
        print(f"❌ Deluge error: {r.json()['error']}")
        return False
    print("✅ Torrent added to Deluge.")
    return True

def list_torrent_matches(query, exclude_keywords=[]):
    print(f"🔍 Searching torrents for: {query}")
    params = {"apikey": JACKETT_API_KEY}

    parts = query.split()
    lang_code = parts[-1].upper()
    lang_keywords = get_language_keywords(lang_code)

    all_results = []

    for lang_kw in lang_keywords:
        new_query = " ".join(parts[:-1] + [lang_kw])
        params["Query"] = new_query
        r = requests.get(JACKETT_URL, params=params)
        r.raise_for_status()
        results = r.json().get("Results", [])
        for result in results:
            title = result.get("Title", "").lower()
            if all(ex.lower() not in title for ex in exclude_keywords):
                # Fix here: check r["magnet"] instead of r["MagnetUri"]
                if not any(r["magnet"] == result["MagnetUri"] for r in all_results):
                    all_results.append({
                        "title": result["Title"],
                        "magnet": result["MagnetUri"]
                    })

    return all_results

def option_search_and_download():
    while True:
        keywords = input("Enter keywords for media search: ").strip()
        exclude = input("Enter negative keywords (space separated): ").strip().lower().split()
        matches = list_torrent_matches(keywords, exclude)

        if not matches:
            print("❌ No suitable torrent found.")
            retry = input("🔁 Try again? (y/n): ").strip().lower()
            if retry == "y":
                continue
            else:
                return

        for i, match in enumerate(matches[:10]):
            print(f"{i}) {match['title']}")
        selected = input("Select torrent number (or press Enter to retry): ").strip()
        if selected.isdigit() and int(selected) < len(matches):
            magnet = matches[int(selected)]["magnet"]
            if add_torrent(magnet):
                print("✅ Download started via Deluge.")
            return
        else:
            print("❌ Invalid selection. Try again.")

def jellyfin_get_headers():
    return {
        "Content-Type": "application/json",
        "X-Emby-Authorization": (
            'MediaBrowser Client="JellyfinTool", '
            'Device="PythonScript", '
            'DeviceId="123456", '
            'Version="1.0", '
            f'Token="{JELLYFIN_API_TOKEN}"'
        )
    }

def get_jellyfin_movies():
    url = f"{JELLYFIN_URL}/Items"
    params = {"IncludeItemTypes": "Movie", "Recursive": "true", "Fields": "MediaSources"}
    headers = jellyfin_get_headers()
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json().get("Items", [])

def search_audio_torrent(movie_name, lang_code):
    # Use the language keyword expansion here too
    lang_keywords = get_language_keywords(lang_code)
    all_matches = []
    for keyword in lang_keywords:
        matches = list_torrent_matches(f"{movie_name} {keyword}")
        all_matches.extend(matches)

    # Remove duplicates
    unique = {}
    for match in all_matches:
        unique[match["magnet"]] = match
    return list(unique.values())

def wait_for_audio_download(expected_filename, timeout=1800):
    print(f"⏳ Waiting for audio file '{expected_filename}' to download...")
    elapsed = 0
    while elapsed < timeout:
        path = os.path.join(DELUGE_DOWNLOAD_FOLDER, expected_filename)
        if os.path.exists(path):
            print("✅ Audio file downloaded!")
            return path
        time.sleep(10)
        elapsed += 10
    print("❌ Timeout waiting for audio.")
    return None

def inject_audio_ffmpeg(video_path, audio_path, lang_code="spa"):
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return False

    output_path = video_path.replace(".mp4", f"_{lang_code}.mkv")
    cmd = [
        "ffmpeg", "-i", video_path, "-i", audio_path,
        "-map", "0", "-map", "1:a:0", "-c", "copy",
        f"-metadata:s:a:1", f"language={lang_code}",
        f"-disposition:a:1", "default", output_path
    ]
    print(f"🎬 Injecting audio with FFmpeg:\n{' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        shutil.move(output_path, video_path)
        print(f"✅ Audio injected into {video_path}")
        return True
    else:
        print(f"❌ FFmpeg error:\n{result.stderr}")
        return False

def refresh_jellyfin_library():
    url = f"{JELLYFIN_URL}/Library/Refresh"
    headers = {"X-Emby-Token": JELLYFIN_API_TOKEN}
    r = requests.post(url, headers=headers)
    print("🔄 Jellyfin library refresh triggered." if r.ok else f"❌ Refresh failed: {r.status_code}")

def inject_audio_auto():
    movies = get_jellyfin_movies()
    for i, m in enumerate(movies):
        print(f"{i}: {m['Name']} ({m.get('ProductionYear', 'N/A')})")
    idx = input("Enter movie number (or 'back' to return): ").strip()
    if idx.lower() == "back":
        return
    if not idx.isdigit() or int(idx) >= len(movies):
        print("❌ Invalid selection.")
        return
    movie = movies[int(idx)]
    movie_path = movie["MediaSources"][0]["Path"]
    movie_name = movie["Name"]
    lang_input = input("Enter 3-letter language code (e.g. SPA, FRA) or 'back' to return: ").strip()
    if lang_input.lower() == "back":
        return
    lang_code = lang_input.upper()

    matches = search_audio_torrent(movie_name, lang_code)
    if not matches:
        print("❌ No audio torrents found.")
        return

    for i, match in enumerate(matches[:10]):
        print(f"{i}) {match['title']}")
    selected = input("Select torrent number (or Enter to cancel): ").strip()
    if not selected.isdigit():
        return

    magnet = matches[int(selected)]["magnet"]
    if not add_torrent(magnet):
        return

    expected_audio_file = f"{movie_name}.{lang_code.lower()}.mka"
    audio_path = wait_for_audio_download(expected_audio_file)
    if not audio_path:
        return

    if inject_audio_ffmpeg(movie_path, audio_path, lang_code.lower()):
        refresh_jellyfin_library()

def inject_audio_manual():
    movies = get_jellyfin_movies()
    for i, m in enumerate(movies):
        print(f"{i}: {m['Name']} ({m.get('ProductionYear', 'N/A')})")
    idx = input("Enter movie number (or 'back' to return): ").strip()
    if idx.lower() == "back":
        return
    if not idx.isdigit() or int(idx) >= len(movies):
        print("❌ Invalid selection.")
        return
    movie = movies[int(idx)]
    movie_path = movie["MediaSources"][0]["Path"]
    lang_input = input("Enter 3-letter language code or 'back' to return: ").strip()
    if lang_input.lower() == "back":
        return
    lang_code = lang_input.upper()
    audio_path = input("Enter full path to audio file (e.g. .aac, .mp3, .wav): ").strip()

    if inject_audio_ffmpeg(movie_path, audio_path, lang_code.lower()):
        refresh_jellyfin_library()

def option_inject_audio():
    print("\n🔧 Audio Injection Options:")
    print("1) 🔄 Auto-download and inject foreign audio")
    print("2) 📂 Inject existing audio file into media")
    sub = input("Choose sub-option (1 or 2): ").strip()
    if sub == "1":
        inject_audio_auto()
    elif sub == "2":
        inject_audio_manual()
    else:
        print("❌ Invalid selection.")

# MAIN MENU
def main():
    while True:
        print("\n🎬 Options:")
        print("1) ➕ Add New Media (Movies, Shows, Documentaries)")
        print("2) 🎧 Inject Foreign Audio (Auto or Manual)")
        print("3) ❌ Exit")
        choice = input("Choose option: ").strip()
        if choice == "1":
            option_search_and_download()
        elif choice == "2":
            option_inject_audio()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option.")

if __name__ == "__main__":
    main()
