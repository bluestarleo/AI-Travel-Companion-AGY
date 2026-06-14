import sqlite3
import os
import json
import urllib.request
import urllib.parse
import time

# Database path definition
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "travel_app.db"))

CITIES = {
    "Rome": {"lat": 41.8902, "lon": 12.4922, "desc": "The capital city of Italy, known for its rich history and ancient ruins."},
    "Paris": {"lat": 48.8584, "lon": 2.2945, "desc": "The capital city of France, famous for art, fashion, gastronomy, and culture."},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917, "desc": "The capital city of Japan, known for ultra-modern technology, skyscrapers, and historic shrines."},
    "San Diego": {"lat": 32.7157, "lon": -117.1611, "desc": "A major city in California known for its beaches, parks, and warm climate."},
    "Beijing": {"lat": 39.9042, "lon": 116.4074, "desc": "The capital city of China, rich in ancient history, palaces, and monuments."},
    "London": {"lat": 51.5074, "lon": -0.1278, "desc": "The capital city of the United Kingdom, famous for its deep royal history and landmarks."}
}

def get_wikipedia_pois(lat: float, lon: float, limit: int = 50) -> list:
    """Queries Wikipedia for nearby articles within 10km."""
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "geosearch",
        "ggscoord": f"{lat}|{lon}",
        "ggsradius": 10000, # 10km search radius
        "ggslimit": limit,
        "prop": "coordinates|pageimages|extracts",
        "pithumbsize": 300,
        "exintro": 1,
        "explaintext": 1,
        "format": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AITravelCompanionBackfill/1.0 (contact: leo.zhu@example.com)"}
    )
    
    try:
        time.sleep(0.5) # rate limit politeness
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if "query" not in data or "pages" not in data["query"]:
                return []
            
            pages = data["query"]["pages"]
            results = []
            for page_id, page in pages.items():
                pid = int(page_id)
                title = page.get("title", "Unknown")
                coords = page.get("coordinates", [{}])[0]
                plat = coords.get("lat", 0.0)
                plon = coords.get("lon", 0.0)
                thumbnail = page.get("thumbnail", {}).get("source")
                extract = page.get("extract", "")
                
                results.append({
                    "pageid": pid,
                    "title": title,
                    "lat": plat,
                    "lon": plon,
                    "url": f"https://en.wikipedia.org/?curid={pid}",
                    "thumbnail": thumbnail,
                    "extract": extract
                })
            return results
    except Exception as e:
        print(f"Error querying Wikipedia: {e}")
        return []

def determine_category_and_popularity(title: str, extract: str) -> tuple:
    """Determines category and a popularity score based on text analysis."""
    text = (title + " " + extract).lower()
    
    # 1. Category heuristics
    category = "Landmark"
    if any(w in text for w in ["museum", "gallery", "exhibition"]):
        category = "Museum"
    elif any(w in text for w in ["church", "cathedral", "basilica", "temple", "shrine", "abbey", "mosque"]):
        category = "Place of Worship"
    elif any(w in text for w in ["park", "garden", "reserve", "wood"]):
        category = "Park & Garden"
    elif any(w in text for w in ["square", "plaza", "piazza"]):
        category = "Square & Plaza"
    elif "bridge" in text:
        category = "Bridge"
    elif any(w in text for w in ["castle", "palace", "tower", "monument", "memorial", "arch", "ruins"]):
        category = "Historic Monument"
    elif any(w in text for w in ["theatre", "theater", "opera", "stadium", "arena"]):
        category = "Entertainment Venue"

    # 2. Popularity calculation (length of Wikipedia extract is a proxy for site prominence)
    char_count = len(extract)
    popularity = min(92.0, max(15.0, char_count / 15.0))
    
    # Boost popularity for highly famous words
    boost_keywords = ["colosseum", "eiffel", "louvre", "vatican", "shrine", "temple", "tower", "palace", "castle", "cathedral", "westminster", "big ben", "senso-ji", "great wall", "forbiden city"]
    if any(k in text for k in boost_keywords):
        popularity = min(99.0, popularity + 15.0)
        
    return category, round(popularity, 1)

def run_direct_backfill():
    print(f"Starting direct Wikipedia-driven backfill for cities using DB: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("Error: Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        for city_name, city_info in CITIES.items():
            print(f"\nProcessing '{city_name}'...")
            
            # Ensure city group exists
            cursor.execute(
                "INSERT OR IGNORE INTO groups (name, description) VALUES (?, ?)",
                (city_name, city_info["desc"])
            )
            cursor.execute("SELECT id FROM groups WHERE name = ?", (city_name,))
            group_id = cursor.fetchone()[0]
            
            # Fetch up to 50 POIs from Wikipedia
            raw_pois = get_wikipedia_pois(city_info["lat"], city_info["lon"], limit=50)
            
            if not raw_pois:
                print(f"No POIs found for {city_name}.")
                continue
                
            # Score and categorize each POI
            evaluated_pois = []
            for poi in raw_pois:
                category, popularity = determine_category_and_popularity(poi["title"], poi["extract"])
                poi["category"] = category
                poi["popularity"] = popularity
                evaluated_pois.append(poi)
                
            # Sort by popularity descending and take the top 30
            sorted_pois = sorted(evaluated_pois, key=lambda x: x["popularity"], reverse=True)[:30]
            
            # Upsert into database
            added_count = 0
            updated_count = 0
            
            for poi in sorted_pois:
                pageid = poi["pageid"]
                title = poi["title"]
                lat = poi["lat"]
                lon = poi["lon"]
                url = poi["url"]
                thumbnail = poi["thumbnail"]
                extract = poi["extract"]
                category = poi["category"]
                popularity = poi["popularity"]
                
                # Check if it already exists
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
                    
            print(f"-> Completed '{city_name}': Added {added_count} new, Updated {updated_count} existing. Total POIs in DB: {len(sorted_pois)}")
            
        conn.commit()
        print("\nBackfill successfully completed!")
    except Exception as e:
        conn.rollback()
        print(f"Backfill transaction error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_direct_backfill()
