# app.py

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from jellyfin_media import get_jellyfin_movies, get_media_file_path
from translate_title import get_translated_title
from jackett_search import search_torrents
from deluge_download import download_torrent
from inject_audio import inject_audio_track

import os

# === FastAPI Setup ===
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
session = {}

# === ROUTES ===

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/movies", response_class=HTMLResponse)
def list_movies(request: Request):
    movies = get_jellyfin_movies()
    return templates.TemplateResponse("movie_list.html", {"request": request, "movies": movies})


@app.post("/select-language", response_class=HTMLResponse)
def select_language(request: Request, movie_id: str = Form(...), title: str = Form(...)):
    session["movie_id"] = movie_id
    session["movie_title"] = title
    return templates.TemplateResponse("language_select.html", {"request": request, "title": title})


@app.post("/search-torrents", response_class=HTMLResponse)
def search_torrents_ui(request: Request, lang_code: str = Form(...)):
    title = session["movie_title"]
    translated_title = get_translated_title(title, lang_code)
    keywords = [title, translated_title, lang_code.lower(), "audio", "dual audio", "dubbed"]
    torrents = search_torrents(keywords)
    session["lang_code"] = lang_code
    session["torrents"] = torrents
    return templates.TemplateResponse("torrent_select.html", {"request": request, "torrents": torrents})


@app.post("/download-torrent", response_class=HTMLResponse)
def download_torrent_ui(request: Request, torrent_index: int = Form(...)):
    selected = session["torrents"][torrent_index]
    audio_path = download_torrent(selected["magnet"])
    session["audio_path"] = audio_path
    return templates.TemplateResponse("manual_audio_inject.html", {"request": request})


@app.post("/inject-audio", response_class=HTMLResponse)
def inject_audio_ui(request: Request, audio_file: str = Form(...)):
    movie_id = session["movie_id"]
    lang_code = session["lang_code"]

    # ✅ Get movie's real file path from Jellyfin
    video_path = get_media_file_path(movie_id)
    if not video_path or not os.path.exists(video_path):
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"❌ Video path not found or does not exist: {video_path}"
        })

    # ✅ Use the manually entered or auto-downloaded audio file
    audio_path = audio_file or session.get("audio_path")
    if not audio_path or not os.path.exists(audio_path):
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "❌ Audio file not found"
        })

    # ✅ Create output file path
    output_path = video_path.replace(".mkv", f".with.{lang_code.lower()}.mkv")

    try:
        inject_audio_track(video_path, audio_path, output_path)
        return templates.TemplateResponse("success.html", {
            "request": request,
            "result": f"✅ Audio injected successfully to: {output_path}"
        })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"❌ Failed to inject audio: {e}"
        })
