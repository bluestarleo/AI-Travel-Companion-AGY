import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "travel_app.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def initialize_database():
    """Initializes the database using the schema.sql file."""
    print(f"Initializing database at: {DB_PATH}")
    
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
        
    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()
        
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.executescript(schema_sql)
        
        # Migration check: Add new columns if table already existed without them
        try:
            cursor.execute("ALTER TABLE articles ADD COLUMN category TEXT;")
        except sqlite3.OperationalError:
            pass # Column already exists
            
        try:
            cursor.execute("ALTER TABLE articles ADD COLUMN popularity REAL DEFAULT 0.0;")
        except sqlite3.OperationalError:
            pass # Column already exists
            
        conn.commit()
        print("Database schema applied successfully.")
    except Exception as e:
        print(f"Error executing schema: {e}")
        conn.rollback()
    finally:
        conn.close()

def add_group(name: str, description: str = "") -> int:
    """Inserts a new group (e.g. City) and returns its ID."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO groups (name, description) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET description=excluded.description",
            (name, description)
        )
        conn.commit()
        # Retrieve the ID
        cursor.execute("SELECT id FROM groups WHERE name = ?", (name,))
        group_id = cursor.fetchone()[0]
        return group_id
    finally:
        conn.close()

def add_article(group_id: int, pageid: int, title: str, lat: float, lon: float, url: str, thumbnail: str = None, extract: str = None, category: str = "Point of Interest", popularity: float = 0.0):
    """Inserts a Wikipedia article associated with a group."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
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
        conn.commit()
    except Exception as e:
        print(f"Error inserting article '{title}': {e}")
    finally:
        conn.close()

def seed_sample_data():
    """Seeds the database with some sample data for Rome and Paris."""
    print("Seeding sample data...")
    
    # 1. Add Rome Group
    rome_id = add_group("Rome", "The capital city of Italy, known for its rich history and ancient ruins.")
    
    # Add articles for Rome
    add_article(
        group_id=rome_id,
        pageid=48480,
        title="Colosseum",
        lat=41.8902,
        lon=12.4922,
        url="https://en.wikipedia.org/?curid=48480",
        thumbnail="https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseum_in_Rome%2C_Italy_-_April_2020.jpg/300px-Colosseum_in_Rome%2C_Italy_-_April_2020.jpg",
        extract="The Colosseum is an elliptical amphitheatre in the centre of the city of Rome, Italy, just east of the Roman Forum.",
        category="Historic Landmark",
        popularity=98.0
    )
    add_article(
        group_id=rome_id,
        pageid=73950,
        title="Trevi Fountain",
        lat=41.9009,
        lon=12.4833,
        url="https://en.wikipedia.org/?curid=73950",
        thumbnail="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Trevi_Fountain%2C_Rome%2C_Italy_-_July_2009.jpg/300px-Trevi_Fountain%2C_Rome%2C_Italy_-_July_2009.jpg",
        extract="The Trevi Fountain is a Roman fountain in the Trevi district in Rome, Italy, designed by Italian architect Nicola Salvi.",
        category="Fountain",
        popularity=95.0
    )

    # 2. Add Paris Group
    paris_id = add_group("Paris", "The capital city of France, famous for art, fashion, gastronomy, and culture.")
    
    # Add articles for Paris
    add_article(
        group_id=paris_id,
        pageid=9232,
        title="Eiffel Tower",
        lat=48.8584,
        lon=2.2945,
        url="https://en.wikipedia.org/?curid=9232",
        thumbnail="https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg/250px-Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",
        extract="The Eiffel Tower is a lattice tower on the Champ de Mars in Paris, France.",
        category="Tower",
        popularity=99.0
    )
    
    print("Database successfully seeded.")

if __name__ == "__main__":
    initialize_database()
    seed_sample_data()
