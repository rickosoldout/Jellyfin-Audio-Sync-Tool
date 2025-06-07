import os
import time
import shutil
import subprocess
import requests
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import quote_plus

# === CONFIG ===
JELLYFIN_URL = "http://192.168.1.178:8096"
JELLYFIN_API_TOKEN = "521425dc932b42e3a07b87dc0c80628b"
JACKETT_API_KEY = "3vn6ers95tws1pj1ep448nhvsjqf56ac"
JACKETT_URL = "http://localhost:9117/api/v2.0/indexers/all/results"
DELUGE_URL = "http://localhost:8112/json"
DELUGE_PASSWORD = "deluge"
DELUGE_DOWNLOAD_FOLDER = "/path/to/deluge/downloads"

LANGUAGE_CODES = {
    "ENG": "eng", "SPA": "spa", "LAT": "spa", "GER": "deu",
    "FRA": "fra", "ARA": "ara", "JPN": "jpn", "CMN": "cmn", "ITA": "ita"
}

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Serve static files (css/js/images if any)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Utility functions ---

def get_language_code(code):
    code = code.strip().upper()
    return LANGUAGE_CODES.get(code, code.lower())

def get_language_keywords(lang_code):
    # More keywords per language for broader torrent search
    lang_code = lang_code.upper()
    mapping = {
        "SPA": ["spanish", "español", "castellano", "spa"],
        "ENG": ["english", "eng", "en"],
        "FRA": ["french", "français", "fra"],
        "GER": ["german", "deutsch", "ger"],
        "ITA": ["italian", "ita", "italiano"],
        "ARA": ["arabic", "ara", "عربى"],
        "JPN": ["japanese", "jpn", "日本語"],
        "CMN": ["mandarin", "cmn", "普通话", "汉语"],
        # add more as needed
    }
    return mapping.get(lang_code, [lang_code.lower()])

def jellyfin_get_headers():
    return {
        "Content-Type": "application/json",
        "X-Emby-Authorization": (
            'MediaBrowser Client="JellyfinTool", '
            'Device="PythonWebUI", '
            'DeviceId="web123", '
            'Version="1.0", '
            f'Token="{JELLYFIN_API_TOKEN}"'
        )
    }

def get_jellyfin_movies():
    url = f"{JELLYFIN_URL}/Items"
    params = {"IncludeItemTypes": "Movie", "Recursive": "true", "Fields": "MediaSources,Path"}
    headers = jellyfin_get_headers()
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json().get("Items", [])

def get_poster_url(item):
    # Compose Jellyfin poster image URL
    # Example: /Items/{ItemId}/Images/Primary
    item_id = item["Id"]
    return f"{JELLYFIN_URL}/Items/{item_id}/Images/Primary?maxHeight=400"

def add_torrent(magnet_link):
    session = requests.Session()
    login_payload = {"method": "auth.login", "params": [DELUGE_PASSWORD], "id": 1}
    r = session.post(DELUGE_URL, json=login_payload)
    if not r.json().get("result", False):
        return False, "Deluge login failed"
    add_payload = {"method": "core.add_torrent_magnet", "params": [magnet_link, {}], "id": 2}
    r = session.post(DELUGE_URL, json=add_payload)
    if r.json().get("error"):
        return False, f"Deluge error: {r.json()['error']}"
    return True, "Torrent added"

def list_torrent_matches(query, exclude_keywords=[]):
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
                if not any(r["magnet"] == result["MagnetUri"] for r in all_results):
                    all_results.append({
                        "title": result["Title"],
                        "magnet": result["MagnetUri"]
                    })
    return all_results

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    movies = get_jellyfin_movies()
    # Prepare data with poster urls
    movies_data = [{
        "id": m["Id"],
        "name": m["Name"],
        "year": m.get("ProductionYear", "N/A"),
        "poster": get_poster_url(m)
    } for m in movies]
    return templates.TemplateResponse("home.html", {"request": request, "movies": movies_data})

@app.get("/search", response_class=HTMLResponse)
async def search_form(request: Request):
    # Show search form to input movie, language, positive and negative keywords
    return templates.TemplateResponse("search.html", {"request": request, "results": None})

@app.post("/search", response_class=HTMLResponse)
async def search_post(
    request: Request,
    movie_name: str = Form(...),
    language_code: str = Form(...),
    negative_keywords: str = Form("")
):
    # Search torrents using movie_name + language_code + negative keywords
    lang_code = language_code.strip().upper()
    negative_list = [k.strip().lower() for k in negative_keywords.split()] if negative_keywords else []
    query = f"{movie_name} {lang_code}"
    try:
        results = list_torrent_matches(query, exclude_keywords=negative_list)
    except Exception as e:
        results = []
        error = str(e)
        return templates.TemplateResponse("search.html", {
            "request": request,
            "results": results,
            "error": error,
            "movie_name": movie_name,
            "language_code": language_code,
            "negative_keywords": negative_keywords
        })

    return templates.TemplateResponse("search.html", {
        "request": request,
        "results": results,
        "movie_name": movie_name,
        "language_code": language_code,
        "negative_keywords": negative_keywords
    })

@app.post("/add_torrent")
async def add_torrent_post(magnet: str = Form(...)):
    success, msg = add_torrent(magnet)
    if success:
        return {"status": "success", "message": msg}
    else:
        raise HTTPException(status_code=400, detail=msg)

# --- Run via: uvicorn app:app --reload
