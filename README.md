# Jellyfin Audio Injector Tool

Welcome to the **Jellyfin Audio Injector Tool**, a powerful and flexible application designed to enhance your Jellyfin media server experience by automating the search, download, and injection of foreign language audio tracks (such as Spanish, but adaptable to any language) into your existing movie and TV show files.

---

## What This Tool Can Do

- **Scan your Jellyfin library** to identify movies or shows missing desired audio tracks.
- **Search for high-quality foreign audio tracks** (Spanish, Latino, Dual Audio, etc.) using Jackett-powered torrent indexers.
- **Download selected torrents** automatically via Deluge BitTorrent client.
- **Extract only the foreign audio streams** from the downloaded files.
- **Inject the foreign audio** seamlessly into your existing media files without affecting the original video or other audio tracks.
- **CLI (Command Line Interface) and Web UI support** for flexible usage.
- **Configurable with environment variables** for easy setup and safe handling of credentials.
- **Easy installation on Ubuntu servers** with automated service setup for continuous running.
- **Supports customization** for different languages, torrent filters, download paths, and Jellyfin servers.

---

## Why Use This Tool?

If you enjoy watching movies or TV shows with audio tracks in your preferred language that are missing from your Jellyfin library, this tool automates a usually manual and technical process:

- No more searching manually for torrents with the right audio.
- No more extracting audio and muxing it into files using complex command-line steps.
- Runs as a service on your home server, so it’s always keeping your library up to date.
- Clean and safe configuration management with `.env` files.
- Friendly CLI and optional web interface.

---

## Who Is This For?

- Jellyfin users wanting multi-language audio tracks.
- Home media server enthusiasts who want more control and automation.
- Anyone comfortable with Python and Linux servers wanting to improve their media experience.

---

## Quick Setup Overview

1. Clone this repository.
2. Create a `.env` file with your Jellyfin URL, API tokens, Deluge credentials, and Jackett URL/key.
3. Install Python dependencies.
4. Run the tool via CLI or web.
5. Optionally set it up as a background service on Ubuntu.

---

## Get Started!

Check out the [Installation](#installation) and [Usage](#usage) sections below to get your Jellyfin Audio Injector up and running.

---

Thanks for checking out the project! Pull requests and issues are welcome.

---

*Ricko Server*
