import requests

def get_translated_title(original_title: str, target_language: str) -> str:
    """
    Use TMDb API to fetch the translated title.
    """
    API_KEY = "your_tmdb_api_key_here"
    base_url = "https://api.themoviedb.org/3"
    
    # Step 1: Search movie by name
    search_url = f"{base_url}/search/movie"
    params = {
        "api_key": fc14706d5679c8296810f1e43f7eac6f,
        "query": original_title,
        "language": "en-US"
    }
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    results = response.json().get("results", [])
    
    if not results:
        return original_title  # fallback
    
    movie_id = results[0]["id"]

    # Step 2: Fetch translations
    translation_url = f"{base_url}/movie/{movie_id}/translations"
    params = {"api_key": API_KEY}
    response = requests.get(translation_url, params=params)
    response.raise_for_status()
    translations = response.json().get("translations", [])

    for entry in translations:
        if entry.get("iso_639_1") == target_language.lower():
            return entry["data"].get("title") or original_title
    
    return original_title  # fallback if translation not found
