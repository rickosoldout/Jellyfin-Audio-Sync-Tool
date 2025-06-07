import requests

def download_torrent(torrent_url, save_path="/downloads"):
    """
    Add a torrent URL to the Deluge Web UI for downloading.
    """
    DELUGE_URL = "http://localhost:8112/json"
    DELUGE_PASSWORD = "deluge"  # change this if your WebUI uses a different password

    session = requests.Session()

    # Step 1: Authenticate
    auth_payload = {
        "method": "auth.login",
        "params": [DELUGE_PASSWORD],
        "id": 1
    }
    auth_response = session.post(DELUGE_URL, json=auth_payload).json()
    if not auth_response.get("result"):
        raise Exception("Failed to authenticate with Deluge Web UI")

    # Step 2: Add the torrent
    add_payload = {
        "method": "core.add_torrent_url",
        "params": [torrent_url, {"download_location": save_path}],
        "id": 2
    }
    response = session.post(DELUGE_URL, json=add_payload).json()
    if "error" in response and response["error"]:
        raise Exception(f"Error adding torrent: {response['error']}")

    return response.get("result", "Torrent added successfully")
