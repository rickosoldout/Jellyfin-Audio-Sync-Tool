import requests
from deluge_client import DelugeRPCClient

# === Configuration ===
JELLYFIN_URL = "http://192.168.1.178:8096"
API_TOKEN = "6f10ca0d453e4a72af132be49476dca1"
USER_ID = "4dcf5bca4868401f8879e526390fed97"

JACKETT_URL = "http://192.168.1.178:9117/api/v2.0/indexers/all/results"
JACKETT_API_KEY = "3vn6ers95tws1pj1ep448nhvsjqf56ac"

DELUGE_HOST = '192.168.1.178'
DELUGE_PORT = 58846
DELUGE_USERNAME = 'username'    # <-- Replace with your Deluge username
DELUGE_PASSWORD = 'password'    # <-- Replace with your Deluge password

HEADERS = {"X-Emby-Token": API_TOKEN}

# === Functions ===

def get_items_by_type(item_type, start_index=0, limit=20):
    """Fetch items from Jellyfin by type (Movie, Series, Documentary)."""
    params = {
        "IncludeItemTypes": item_type,
        "Recursive": "true",
        "StartIndex": start_index,
        "Limit": limit
    }
    url = f"{JELLYFIN_URL}/Users/{USER_ID}/Items"
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json().get("Items", [])
    else:
        print(f"Error fetching {item_type}: {response.status_code} - {response.text}")
        return []

def paginate_items(item_type):
    """Paginate through items and let user pick by number or type exact name."""
    start = 0
    limit = 20

    while True:
        items = get_items_by_type(item_type, start, limit)
        if not items:
            if start == 0:
                print(f"No {item_type}s found.")
            return None

        current_titles = [item['Name'] for item in items]

        for idx, item in enumerate(items, start=start+1):
            print(f"{idx}. {item['Name']}")

        user_input = input("\nType the exact name, number to select, 'more' to load more, or 'exit': ").strip()

        if user_input.lower() == "more":
            start += limit
        elif user_input.lower() == "exit":
            return None
        elif user_input.isdigit():
            index = int(user_input) - 1
            if start <= index < start + len(current_titles):
                return current_titles[index - start]
            else:
                print("Invalid number. Try again.")
        elif user_input in current_titles:
            return user_input
        else:
            print("Invalid input. Please try again.\n")

def search_jackett(query):
    """Search Jackett for torrents matching multiple Spanish keywords."""
    search_keywords = [query, "spanish", "spanish audio", "español", "esp"]
    combined_results = []

    for keyword in search_keywords:
        params = {
            "apikey": JACKETT_API_KEY,
            "Query": keyword
        }
        response = requests.get(JACKETT_URL, params=params)
        if response.status_code == 200:
            results = response.json()
            combined_results.extend(results.get("Results", []))
        else:
            print(f"Jackett search error: {response.status_code} - {response.text}")
            return []

    # Remove duplicates by title
    seen_titles = set()
    unique_results = []
    for item in combined_results:
        title = item.get("Title")
        if title not in seen_titles:
            seen_titles.add(title)
            unique_results.append(item)

    if not unique_results:
        print("No results found.")
        return []

    # Print results with numbers
    for i, item in enumerate(unique_results, 1):
        print(f"{i}. {item.get('Title')}")

    # Let user pick which torrent to add
    while True:
        choice = input("Enter number to download torrent or 'exit' to cancel: ").strip()
        if choice.lower() == 'exit':
            return None
        if choice.isdigit():
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(unique_results):
                selected_torrent = unique_results[choice_idx]
                magnet_link = selected_torrent.get("Link") or selected_torrent.get("MagnetUri") or selected_torrent.get("Guid")
                if magnet_link:
                    return magnet_link
                else:
                    print("Magnet link not found for this torrent.")
                    return None
            else:
                print("Invalid number, try again.")
        else:
            print("Invalid input, please enter a number or 'exit'.")

def add_torrent_to_deluge(magnet_link):
    """Connect to Deluge and add the torrent magnet link."""
    client = DelugeRPCClient(DELUGE_HOST, DELUGE_PORT, DELUGE_USERNAME, DELUGE_PASSWORD)
    try:
        client.connect()
        client.call('core.add_torrent_magnet', magnet_link, {})
        print("Torrent added to Deluge!")
    except Exception as e:
        print(f"Failed to add torrent to Deluge: {e}")

def main():
    print("📺 What do you want to browse?")
    print("1. Movies")
    print("2. Series")
    print("3. Documentaries")

    choice = input("Enter 1, 2, or 3: ").strip()
    item_type_map = {"1": "Movie", "2": "Series", "3": "Documentary"}

    if choice not in item_type_map:
        print("Invalid choice. Exiting.")
        return

    selected_type = item_type_map[choice]
    print(f"\n📥 Fetching your {selected_type}s...\n")

    selected_title = paginate_items(selected_type)
    if selected_title:
        print(f"\n🔍 Searching Jackett for '{selected_title}' with Spanish audio keywords...\n")
        magnet_link = search_jackett(selected_title)
        if magnet_link:
            add_torrent_to_deluge(magnet_link)
        else:
            print("No torrent added.")
    else:
        print("No title selected. Goodbye!")

if __name__ == "__main__":
    main()
