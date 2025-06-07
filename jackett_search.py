import feedparser
import urllib.parse

def search_torrents(media_title, required_keywords=None, exclude_keywords=None):
    if required_keywords is None:
        required_keywords = []
    if exclude_keywords is None:
        exclude_keywords = []

    query = media_title
    for kw in required_keywords:
        query += f' {kw}'

    base_url = 'http://localhost:9117'  # Jackett URL
    api_key = '3vn6ers95tws1pj1ep448nhvsjqf56ac'       # Replace with your Jackett API key
    indexer_id = 'all'                  # Use 'all' or your preferred indexer

    search_url = f'{base_url}/api/v2.0/indexers/{indexer_id}/results/torznab/api?apikey={api_key}&t=search&q={urllib.parse.quote(query)}'

    print(f"📡 Searching Jackett at: {search_url}")
    feed = feedparser.parse(search_url)

    results = []
    for entry in feed.entries:
        title = entry.title.lower()

        if any(ex_kw.lower() in title for ex_kw in exclude_keywords):
            continue
        if all(req_kw.lower() in title for req_kw in required_keywords):
            results.append({
                'title': entry.title,
                'magnet': entry.link,
                'size': entry.get('size', 'unknown')
            })

    return results
