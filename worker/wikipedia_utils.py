import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any

def get_nearby_wikipedia_articles(
    lat: float, 
    lon: float, 
    radius_meters: int = 1000, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for Wikipedia articles near the specified geographic coordinates.

    Args:
        lat (float): The latitude of the center point.
        lon (float): The longitude of the center point.
        radius_meters (int, optional): The search radius in meters. Defaults to 1000. Max is 10000.
        limit (int, optional): The maximum number of results to return. Defaults to 10. Max is 500.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing nearby articles.
            Each dictionary contains:
            - pageid (int): Wikipedia Page ID.
            - title (str): Title of the article.
            - lat (float): Latitude of the article.
            - lon (float): Longitude of the article.
            - url (str): Link to the Wikipedia page.
            - thumbnail (str | None): URL to the article's representative image.
            - extract (str | None): Plain text intro/summary of the page.
    """
    base_url = "https://en.wikipedia.org/w/api.php"
    
    # MediaWiki query parameters using geosearch generator to fetch rich metadata
    params = {
        "action": "query",
        "generator": "geosearch",
        "ggscoord": f"{lat}|{lon}",
        "ggsradius": min(max(radius_meters, 1), 10000), # Constrain radius to 1m - 10000m
        "ggslimit": min(max(limit, 1), 500),          # Constrain limit to 1 - 500
        "prop": "coordinates|pageimages|extracts",
        "pithumbsize": 300,
        "exintro": 1,
        "explaintext": 1,
        "format": "json"
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    # Custom User-Agent to respect Wikimedia policy
    headers = {
        "User-Agent": "AITravelCompanionBot/1.0 (contact: leo.zhu@example.com)"
    }
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if "query" not in data or "pages" not in data["query"]:
                return []
                
            pages = data["query"]["pages"]
            results = []
            
            for page_id, page in pages.items():
                pid = int(page_id)
                title = page.get("title", "Unknown")
                
                # Fetch coordinates from response
                coords = page.get("coordinates", [{}])[0]
                page_lat = coords.get("lat", 0.0)
                page_lon = coords.get("lon", 0.0)
                
                thumbnail_url = page.get("thumbnail", {}).get("source")
                extract = page.get("extract")
                
                results.append({
                    "pageid": pid,
                    "title": title,
                    "lat": page_lat,
                    "lon": page_lon,
                    "url": f"https://en.wikipedia.org/?curid={pid}",
                    "thumbnail": thumbnail_url,
                    "extract": extract.strip() if extract else None
                })
                
            return results
            
    except Exception as e:
        print(f"Error fetching Wikipedia geosearch results: {e}")
        return []
