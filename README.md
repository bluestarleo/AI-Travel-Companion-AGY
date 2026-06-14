# AI Travel Companion

An interactive travel companion application that uses an AI agent to fetch points of interest for cities from Wikipedia, stores them in a local SQLite database, and displays them on a frontend dashboard map.

## 📂 Project Structure

This is a monorepo containing three main components:

*   **`client/`**: A React frontend built with **Next.js** (TypeScript, Tailwind CSS). It serves the user interface, renders interactive maps, and displays information about cities and articles.
*   **`worker/`**: Python utility scripts and a scraper agent powered by the Antigravity SDK (`agent.py`) that queries the Wikipedia GeoSearch APIs and seeds details about points of interest into the database.
*   **`database/`**: Stores the local SQLite database (`travel_app.db`) and SQL schema files.

---

## 🛠️ Getting Started

### 1. Prerequisites

Make sure you have the following installed:
*   [Node.js](https://nodejs.org/) (v18+)
*   [Python 3.10+](https://www.python.org/)
*   An API Key for Gemini (`GEMINI_API_KEY`) if running the Python agent.

### 2. Environment Setup

Create a `.env` file in the root directory (or update the existing one) and add your API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## ⚙️ Running the Components

### Step A: Provision the Database
Before running the UI, initialize the SQLite database using Python:

```bash
# Navigate to database directory
cd database

# Run script to create database tables and seed initial data
python init_db.py
```

### Step B: Populate the Database with More Cities (Optional)
You can run the Python scraper agent to automatically pull points of interest for any city (e.g., "San Diego", "Tokyo", etc.) and populate the database:

```bash
# Navigate to the worker directory
cd ../worker

# Install requirements (ensure standard packages like python-dotenv and google-antigravity are installed)
pip install python-dotenv

# Run the agent for a specific city
python agent.py "San Diego"
```

### Step C: Run the Next.js Frontend
Once the database has data, you can start the development server for the UI:

```bash
# Navigate to the client directory
cd ../client

# Install frontend dependencies
npm install

# Start the local development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

---

## 🔌 How Frontend & Backend Connect

1.  **Data Generation (Python)**: `worker/agent.py` pulls data from the Wikipedia GeoSearch API and stores it in the local SQLite database (`database/travel_app.db`).
2.  **Data Consumption (Next.js)**: The `client` Next.js server connects directly to the local SQLite database file `../database/travel_app.db` to read and render the city points of interest onto the interactive browser map.
