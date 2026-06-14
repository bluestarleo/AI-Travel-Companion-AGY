-- Create groups table (e.g., cities)
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create articles table (Wikipedia points of interest)
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
    category TEXT,
    popularity REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);

-- Index coordinates and foreign keys for quick lookup
CREATE INDEX IF NOT EXISTS idx_articles_group_id ON articles(group_id);
CREATE INDEX IF NOT EXISTS idx_articles_coords ON articles(lat, lon);
