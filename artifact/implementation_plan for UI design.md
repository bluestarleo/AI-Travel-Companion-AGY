# Travel Companion UI Implementation Plan

This plan describes the design, components, and routing architecture for the Next.js travel companion client app. It includes database connections, an interactive Leaflet map component, and dynamic Wikipedia API integration.

## User Review Required

Please review the routing, styling choices, and the Leaflet map implementation details.

> [!NOTE]
> **Map Component**: We are using **Leaflet** (`react-leaflet`), which is an open-source map library. It runs fully client-side without requiring any external map API keys (like Google Maps or Mapbox).

## Proposed Changes

We will create/modify the following files in the `client/` workspace:

```
client/src/
├── lib/
│   └── db.ts (database connection helper)
├── components/
│   ├── MapComponent.tsx (interactive map client component)
│   └── MapWrapper.tsx (SSR-safe dynamic loader for map)
└── app/
    ├── globals.css (styles update)
    ├── page.tsx (Homepage: city list browser)
    ├── city/
    │   └── [id]/
    │       └── page.tsx (City Page: POI sidebar + interactive map)
    └── article/
        └── [pageid]/
            └── page.tsx (Article Page: rich POI details from Wikipedia API)
```

---

### 1. Database Integration

#### [NEW] [db.ts](file:///c:/Users/leo.zhu/OneDrive%20-%20CBRE,%20Inc/ai-travel-companion/client/src/lib/db.ts)
A backend utility to connect to the SQLite database `travel_app.db` located at `../database/travel_app.db` relative to the client app.
```typescript
import Database from 'better-sqlite3';
import path from 'path';

const dbPath = path.resolve(process.cwd(), '../database/travel_app.db');
export const db = new Database(dbPath, { readonly: true });

export interface CityGroup {
  id: number;
  name: string;
  description: string;
  created_at: string;
  article_count?: number;
}

export interface Article {
  id: number;
  pageid: number;
  group_id: number;
  title: string;
  lat: number;
  lon: number;
  url: string;
  thumbnail: string | null;
  extract: string | null;
}
```

---

### 2. Map Components (Client-Side Only)

Because Leaflet interacts with the browser's `window` object, it must be loaded dynamically without Server-Side Rendering (SSR).

#### [NEW] [MapComponent.tsx](file:///c:/Users/leo.zhu/OneDrive%20-%20CBRE,%20Inc/ai-travel-companion/client/src/components/MapComponent.tsx)
A client-side Leaflet map component that shows marker pins for all articles in a city, supports clicking pins to show popups, and updates center/zoom when clicking a sidebar item.

#### [NEW] [MapWrapper.tsx](file:///c:/Users/leo.zhu/OneDrive%20-%20CBRE,%20Inc/ai-travel-companion/client/src/components/MapWrapper.tsx)
Uses Next.js `dynamic()` helper with `{ ssr: false }` to safely load `MapComponent` on the client.

---

### 3. Application Routing and Styling

#### [MODIFY] [globals.css](file:///c:/Users/leo.zhu/OneDrive%20-%20CBRE,%20Inc/ai-travel-companion/client/src/app/globals.css)
Add Leaflet's stylesheet imports and add custom CSS themes/animations for a premium dark/glassmorphic look.

#### [MODIFY] [page.tsx](file:///c:/Users/leo.zhu/OneDrive%20-%20CBRE,%20Inc/ai-travel-companion/client/src/app/page.tsx)
Homepage designed with a premium card grid displaying available cities (Rome, Paris, Tokyo) retrieved from the database, along with their POI counts.

#### [NEW] [page.tsx (City Page)](file:///c:/Users/leo.zhu/OneDrive%20-%20CBRE,%20Inc/ai-travel-companion/client/src/app/city/%5Bid%5D/page.tsx)
City page splitting the view:
* **Left sidebar (35%)**: Displays city name, description, and list of points of interest.
* **Right view (65%)**: Renders the Leaflet map with coordinates pinned. Selecting an item in the sidebar focuses the map on that pin.

#### [NEW] [page.tsx (Article Page)](file:///c:/Users/leo.zhu/OneDrive%20-%20CBRE,%20Inc/ai-travel-companion/client/src/app/article/%5Bpageid%5D/page.tsx)
Retrieves the Wikipedia Page ID from the URL, queries the live Wikipedia MediaWiki API for the full HTML extract and high-resolution thumbnail images, and renders a rich article view.

---

## Verification Plan

### Automated Tests
- Run `npm run build` from the workspace root to verify compilation of all TypeScript code and dynamic map loading.

### Manual Verification
- Start `npm run dev` and test:
  1. Navigating from the homepage to Rome/Paris/Tokyo.
  2. Clicking pins on the map, viewing popups, and clicking through to the article page.
  3. Viewing the full Wikipedia content on the article page and using the back button.
