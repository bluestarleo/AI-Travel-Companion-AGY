import asyncio
import sys
import os
import sqlite3
import urllib.request
import urllib.parse
import json
import time
from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig

# Load environment variables (such as GEMINI_API_KEY)
load_dotenv()

# Database path definition
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "travel_app.db"))

# =====================================================================
# Custom Tools for the Agent
# =====================================================================

def get_city_coordinates(city: str) -> str:
    """
    Query Wikipedia to retrieve the geographical coordinates (latitude and longitude) of a city.
    
    Args:
        city (str): The name of the city (e.g. 'Rome', 'Paris').
        
    Returns:
        str: Coordinates formatted as 'latitude|longitude', or an error message.
    """
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "coordinates",
        "titles": city,
        "format": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AITravelCompanionAgent/1.0 (contact: leo.zhu@example.com)"}
    )
    
    try:
        # Respect rate limits between tool executions
        time.sleep(1)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                if "coordinates" in page:
                    coords = page["coordinates"][0]
                    lat = coords["lat"]
                    lon = coords["lon"]
                    return f"{lat}|{lon}"
            return f"Error: Coordinates for city '{city}' could not be resolved from Wikipedia."
    except Exception as e:
        return f"Error querying coordinates: {e}"


def get_nearby_places(coord_str: str, radius_meters: int = 2000, limit: int = 10) -> str:
    """
    Find Wikipedia articles/points of interest near the specified coordinates.
    
    Args:
        coord_str (str): The center coordinates formatted as 'latitude|longitude' (e.g., '41.8933|12.4827').
        radius_meters (int): The search radius in meters (max 10000).
        limit (int): The maximum number of results to return (max 50).
        
    Returns:
        str: A JSON string containing a list of articles with their details.
    """
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "geosearch",
        "ggscoord": coord_str,
        "ggsradius": min(max(radius_meters, 1), 10000),
        "ggslimit": min(max(limit, 1), 50),
        "prop": "coordinates|pageimages|extracts",
        "pithumbsize": 300,
        "exintro": 1,
        "explaintext": 1,
        "format": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AITravelCompanionAgent/1.0 (contact: leo.zhu@example.com)"}
    )
    
    try:
        # Respect rate limits between tool executions
        time.sleep(1)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if "query" not in data or "pages" not in data["query"]:
                return "[]"
                
            pages = data["query"]["pages"]
            results = []
            for page_id, page in pages.items():
                pid = int(page_id)
                title = page.get("title", "Unknown")
                coords = page.get("coordinates", [{}])[0]
                lat = coords.get("lat", 0.0)
                lon = coords.get("lon", 0.0)
                thumbnail = page.get("thumbnail", {}).get("source")
                extract = page.get("extract", "")
                
                results.append({
                    "pageid": pid,
                    "title": title,
                    "lat": lat,
                    "lon": lon,
                    "url": f"https://en.wikipedia.org/?curid={pid}",
                    "thumbnail": thumbnail,
                    "extract": extract
                })
            return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error fetching nearby places: {e}"


def add_places_to_database(city_name: str, articles_json: str) -> str:
    """
    Insert a list of point of interest articles into the SQLite database associated with the given city.
    
    Args:
        city_name (str): The name of the city (e.g. 'Rome') to group these articles under.
        articles_json (str): A JSON string containing a list of dictionaries with the articles' keys:
                            'pageid', 'title', 'lat', 'lon', 'url', 'thumbnail', and 'extract'.
        
    Returns:
        str: Success or error status message.
    """
    if not os.path.exists(DB_PATH):
        return f"Error: SQLite database does not exist at '{DB_PATH}'. Please initialize it first."
        
    try:
        articles = json.loads(articles_json)
    except Exception as e:
        return f"Error: Invalid JSON payload format: {e}"
        
    if not isinstance(articles, list):
        return "Error: Expecting articles_json to represent a list of articles."

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Ensure group (city) exists and get its ID
        cursor.execute(
            "INSERT OR IGNORE INTO groups (name, description) VALUES (?, ?)", 
            (city_name, f"City group for {city_name} managed by agent.")
        )
        cursor.execute("SELECT id FROM groups WHERE name = ?", (city_name,))
        group_id = cursor.fetchone()[0]
        
        # 2. Insert all articles in batch
        added_count = 0
        updated_count = 0
        for article in articles:
            pageid = article.get("pageid")
            title = article.get("title")
            lat = article.get("lat")
            lon = article.get("lon")
            url = article.get("url")
            thumbnail = article.get("thumbnail")
            extract = article.get("extract")
            category = article.get("category", "Point of Interest")
            popularity = article.get("popularity", 0.0)
            
            if not pageid or not title or lat is None or lon is None or not url:
                continue
                
            # Check if POI already exists in the database
            cursor.execute("SELECT 1 FROM articles WHERE pageid = ?", (pageid,))
            exists = cursor.fetchone() is not None
            
            cursor.execute(
                """
                INSERT INTO articles (pageid, group_id, title, lat, lon, url, thumbnail, extract, category, popularity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(pageid) DO UPDATE SET
                    group_id=excluded.group_id,
                    title=excluded.title,
                    lat=excluded.lat,
                    lon=excluded.lon,
                    url=excluded.url,
                    thumbnail=excluded.thumbnail,
                    extract=excluded.extract,
                    category=excluded.category,
                    popularity=excluded.popularity
                """,
                (pageid, group_id, title, lat, lon, url, thumbnail, extract, category, popularity)
            )
            
            if exists:
                updated_count += 1
            else:
                added_count += 1
            
        conn.commit()
        return f"Successfully processed city '{city_name}': added {added_count} new POIs, updated {updated_count} existing POIs."
    except Exception as e:
        conn.rollback()
        return f"Database transaction error: {e}"
    finally:
        conn.close()

# =====================================================================
# Main Agent Loop
# =====================================================================

async def run_agent(city: str):
    print(f"Initializing Antigravity Agent for city: {city}...")
    
    # System Instructions optimized for finding, categorizing, and ranking the top 30 tourist POIs
    system_instructions = (
        "You are an autonomous travel research agent.\n"
        f"Your goal is to find the most popular travel sights/points of interest for a given city and populate the SQLite database.\n"
        f"The SQLite database is located at: {DB_PATH}\n\n"
        "Available Tools:\n"
        "1. get_city_coordinates: Resolve a city name to its latitude and longitude. Returns 'lat|lon'.\n"
        "2. get_nearby_places: Query Wikipedia for articles/points of interest around a set of coordinates. Returns a JSON list.\n"
        "3. add_places_to_database: Insert a batch list of articles into the SQLite database. "
        "Expects the city name as `city_name` and the exact JSON string of articles as `articles_json`.\n\n"
        "Workflow:\n"
        "- First, resolve coordinates for the city.\n"
        "- Next, query nearby articles using those coordinates (suggested radius 5000m to 10000m, limit 50 articles to capture a wide range of sites).\n"
        "- From the returned places, analyze their names and descriptions to filter out non-tourist spots (like local high schools, offices, minor metro stations, etc.).\n"
        "- Select the top ~30 most popular tourist points of interest (major landmarks, sights, historic buildings, cathedrals, museums, parks, squares) based on global fame and significance.\n"
        "- If the query returns fewer than 30 quality spots, store what is available.\n"
        "- For each selected POI, add/enhance the following fields in the JSON:\n"
        "  - `category`: A short descriptive category (e.g. 'Monument', 'Museum', 'Park', 'Cathedral', 'Bridge', 'Square').\n"
        "  - `popularity`: A rating/ranking signal score between 0.0 and 100.0, where 100.0 is the most famous/visited (e.g., Eiffel Tower or Colosseum would be 98-100; smaller regional museums or parks would be lower).\n"
        "- Pass the final compiled JSON list of the top ~30 POIs to `add_places_to_database` in a single call.\n"
        "- Finally, output a brief confirmation message outlining what you added."
    )
    
    config = LocalAgentConfig(
        system_instructions=system_instructions,
        tools=[get_city_coordinates, get_nearby_places, add_places_to_database]
    )
    
    async with Agent(config) as agent:
        prompt = f"Find the top 30 most popular travel sights/points of interest for {city}, assign them categories and popularity scores, and save them to the database."
        print(f"Sending prompt to agent: '{prompt}'")
        response = await agent.chat(prompt)
        print("\nAgent Output:")
        print(await response.text())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent.py <city_name>")
        sys.exit(1)
        
    city_name = sys.argv[1]
    
    # Run the async agent loop
    asyncio.run(run_agent(city_name))
