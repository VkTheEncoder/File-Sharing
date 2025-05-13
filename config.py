# fetcher.py

import requests
import asyncio

# Base URL for the public Consumet “gogoanime” API
BASE_API = "https://api.consumet.org/anime/gogoanime"

# A browser‐style header so we don’t get throttled
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}


def _sync_search(query: str) -> list[dict]:
    """
    Call the gogoanime search endpoint:
      GET /search?keyw=<query>
    Returns [{"id": "<slug>", "name": "<title>"}, …]
    """
    resp = requests.get(
        f"{BASE_API}/search",
        params={"keyw": query},
        headers=HEADERS,
        timeout=10
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    out = []
    for item in results[:5]:
        out.append({
            "id":   item["id"],          # e.g. "raven-of-the-inner-palace"
            "name": item["title"]        # e.g. "Raven of the Inner Palace"
        })
    return out


async def search_anime(query: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_search, query)


def _sync_fetch_episodes(anime_id: str) -> list[dict]:
    """
    Call the gogoanime info endpoint:
      GET /info/{anime_id}
    which returns {"episodes":[{"id":"<epId>","episode":"1",...},…]}
    We map that to [{"episodeId":epId,"number":episode,"title":""}, …].
    """
    resp = requests.get(
        f"{BASE_API}/info/{anime_id}",
        headers=HEADERS,
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json().get("episodes", [])
    out = []
    for ep in data:
        out.append({
            "episodeId": ep["id"],       # consumet’s episode slug
            "number":    ep["episode"],  # "1", "2", …
            "title":     ""              # gogoanime doesn’t give per‐ep titles
        })
    return out


async def fetch_episodes(anime_id: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_fetch_episodes, anime_id)


def fetch_tracks(episode_id: str) -> list[dict]:
    """
    (No change) – you can implement subtitle logic here if/when you have it.
    """
    return []


def fetch_sources_and_referer(episode_id: str) -> tuple[list[dict], str, str]:
    """
    Call the gogoanime watch endpoint:
      GET /watch?episodeId=<episode_id>
    It returns {"sources":[{"url":"...m3u8",...},…], …}
    """
    resp = requests.get(
        f"{BASE_API}/watch",
        params={"episodeId": episode_id},
        headers=HEADERS,
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    sources = data.get("sources", [])
    # There’s no special referer or cookie needed – gogoanime’s API URLs don’t expire
    return sources, "", ""
