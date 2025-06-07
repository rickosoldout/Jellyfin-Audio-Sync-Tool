import requests

API_KEY = "3vn6ers95tws1pj1ep448nhvsjqf56ac"  # Your Jackett API key

def search_jackett(query):
    url = "http://localhost:9117/api/v2.0/indexers/all/results"
    params = {
        "apikey": API_KEY,
        "Query": query
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json()
        for item in results.get("Results", []):
            title = item.get("Title")
            download_url = item.get("Link")  # Torrent or magnet link
            print(f"Title: {title}")
            print(f"Download Link: {download_url}")
            print("-" * 40)
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    movie_name = input("Enter movie name and language (e.g. 'Oppenheimer Spanish audio'): ")
    search_jackett(movie_name)
