# SQLite Database Configuration & Provisioning Guide

We have set up a SQLite database inside the `database/` folder of your monorepo. This allows you to store Wikipedia articles (points of interest) and associate each one with a group (such as a City).

---

## 1. Database Schema (`schema.sql`)

The database consists of two tables:
1. **`groups`**: Stores groups (e.g. cities like Rome or Paris).
2. **`articles`**: Stores Wikipedia articles with coordinates, summaries, and URLs, mapped to a group via a foreign key relationship.

```sql
-- groups table (e.g., cities)
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- articles table (Wikipedia points of interest)
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pageid INTEGER UNIQUE NOT NULL,
    group_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    url TEXT NOT NULL,
    thumbnail TEXT,
    extract TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);
```

---

## 2. Provisioning Script (`init_db.py`)

A python script [init_db.py](file:///c:/Users/leo.zhu/OneDrive%20-%20CBRE,%20Inc/ai-travel-companion/database/init_db.py) has been provided to build and seed the database. 

It does the following:
1. Creates the SQLite database file `travel_app.db` at `database/travel_app.db`.
2. Applies the `schema.sql` script (including foreign key enforcement `PRAGMA foreign_keys = ON;`).
3. Seeds the tables with sample records for **Rome** (Colosseum, Trevi Fountain) and **Paris** (Eiffel Tower).

### Running the Provisioning Script
To initialize or reset the database, run this command from the monorepo root:
```bash
python database/init_db.py
```

---

## 3. Querying the Database (Python Example)

Here is a Python helper example to fetch all articles grouped under a specific city:

```python
import sqlite3

def get_articles_by_city(city_name: str):
    conn = sqlite3.connect("database/travel_app.db")
    cursor = conn.cursor()
    
    query = """
        SELECT a.title, a.lat, a.lon, a.url, a.extract 
        FROM articles a
        JOIN groups g ON a.group_id = g.id
        WHERE g.name = ?
    """
    
    cursor.execute(query, (city_name,))
    rows = cursor.fetchall()
    conn.close()
    
    return rows

# Example run:
rome_places = get_articles_by_city("Rome")
for place in rome_places:
    print(f"Name: {place[0]} | Coords: ({place[1]}, {place[2]}) | URL: {place[3]}")
```
