import sqlite3
import os
import asyncio
from agent import run_agent

# Database path definition
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "travel_app.db"))

async def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: SQLite database does not exist at '{DB_PATH}'. Initialize it first.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM groups ORDER BY id ASC")
        cities = cursor.fetchall()
    except Exception as e:
        print(f"Error reading cities from database: {e}")
        return
    finally:
        conn.close()

    if not cities:
        print("No cities found in database to backfill.")
        return

    city_names = [city[1] for city in cities]
    print(f"[Backfill] Found {len(cities)} cities in database to backfill: {', '.join(city_names)}")
    print("[Backfill] Starting batch backfill process. Fetching the top ~30 POIs for each city...")

    for city_id, city_name in cities:
        # Check current count of POIs for this city
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles WHERE group_id = ?", (city_id,))
        poi_count = cursor.fetchone()[0]
        conn.close()

        if poi_count >= 25:
            print(f"[Backfill] Skipping '{city_name}' (already has {poi_count} POIs).")
            continue

        print("\n" + "=" * 80)
        print(f"[Backfill] Starting research and update for: {city_name} (ID: {city_id}, current POIs: {poi_count})")
        print("=" * 80)
        
        try:
            # Execute agent to query, categorize, rank and upsert POIs
            await run_agent(city_name)
            print(f"[Backfill] Success: Completed backfill for {city_name}.")
            
            # Rate limit buffer
            print("[Backfill] Sleeping for 15 seconds to avoid API rate limits...")
            await asyncio.sleep(15)
        except Exception as e:
            print(f"[Backfill] Error: Failed to run agent for {city_name}: {e}")

    print("\n" + "=" * 80)
    print("[Backfill] Batch backfill process finished.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
