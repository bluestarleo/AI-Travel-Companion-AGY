# Wikipedia Geolocation Search (Geosearch) API

The Wikipedia Geosearch API allows you to retrieve articles/points of interest near specified geographic coordinates. By using the API's **generator** feature, you can retrieve pages, their coordinates, descriptive extracts, and images in a single round-trip HTTP request.

---

## 1. API Endpoint & Core Parameters

* **Base URL**: `https://en.wikipedia.org/w/api.php`
* **Format**: All queries should include `format=json` to return data in JSON format.

### Geosearch Parameters

When using `list=geosearch` (returns page IDs/titles only) or `generator=geosearch` (returns page details via properties), the following parameters filter results:

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `gscoord` / `ggscoord` | String | **Yes** | Center coordinates of the search formatted as `latitude\|longitude` (e.g. `48.8584\|2.2945`). |
| `gsradius` / `ggsradius` | Integer | **Yes** | Search radius in meters. Maximum is `10000` (10 km). |
| `gslimit` / `ggslimit` | Integer | No | Max results to return. Default is `10`, max is `500`. |

> [!NOTE]
> When using `generator=geosearch`, all parameters must be prefixed with `ggs` (e.g., `ggscoord`, `ggsradius`, `ggslimit`) instead of `gs` to distinguish them from standard query parameters.

---

## 2. Advanced: Querying Rich Page Data

To find points of interest with summaries and photos, combine the `geosearch` generator with page properties:

```http
GET https://en.wikipedia.org/w/api.php?action=query&generator=geosearch&ggscoord=48.8584|2.2945&ggsradius=1000&ggslimit=5&prop=coordinates|pageimages|extracts&pithumbsize=250&exintro=1&explaintext=1&format=json
```

### Key Property Parameters
* `prop=coordinates|pageimages|extracts`: Returns coordinates, thumbnail image info, and page text summaries.
* `pithumbsize=250`: Specifies image thumbnail width in pixels (necessary to get a direct image URL in `thumbnail.source`).
* `exintro=1` & `explaintext=1`: Limits extracts to introductory sentences and cleans out HTML tags/markup (returns plain text).

---

## 3. How to Test (cURL & PowerShell)

### Using cURL
```bash
curl -s "https://en.wikipedia.org/w/api.php?action=query&generator=geosearch&ggscoord=48.8584|2.2945&ggsradius=1000&ggslimit=3&prop=coordinates|pageimages|extracts&pithumbsize=250&exintro=1&explaintext=1&format=json"
```

### Using PowerShell
```powershell
$uri = "https://en.wikipedia.org/w/api.php?action=query&generator=geosearch&ggscoord=48.8584|2.2945&ggsradius=1000&ggslimit=3&prop=coordinates|pageimages|extracts&pithumbsize=250&exintro=1&explaintext=1&format=json"
Invoke-RestMethod -Uri $uri -Method Get
```

---

## 4. Live API Test Execution

The following live results were retrieved by running a sample geosearch around the **Eiffel Tower (48.8584, 2.2945)** with a radius of **1000 meters**:

<!-- LIVE_RESULTS_START -->
### Eiffel Tower
- **Coordinates**: (48.85822222, 2.2945)
![Eiffel Tower](https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg/250px-Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg)
- **Summary**: The Eiffel Tower (  EYE-fəl; French: Tour Eiffel [tuʁ ɛfɛl] ) is a lattice tower on the Champ de Mars in Paris, France. It is named after the engineer Gustave Eiffel, whose company designed and built the tower from 1887 to 1889.
Locally nicknamed "La dame de fer" (French for "Iron Lady") for its ...

---

### Pont d'Iéna
- **Coordinates**: (48.85972222, 2.29222222)
- **Summary**: Pont d'Iéna (French: [pɔ̃ djena]; French for 'Jena Bridge') is a bridge spanning the River Seine in Paris. It links the Eiffel Tower on the Left Bank to the district of Trocadéro on the Right Bank.

---

### Globe Céleste
- **Coordinates**: (48.8575, 2.29277778)
![Globe Céleste](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Tour_Eiffel_et_le_Globe_C%C3%A9leste.jpg/250px-Tour_Eiffel_et_le_Globe_C%C3%A9leste.jpg)
- **Summary**: The Globe Céleste was an icon of the Exposition Universelle of 1900 in Paris, similar to the Eiffel Tower. It was constructed in the shape of a large globe and stood close to the Eiffel Tower. It was in the form of a blue and gold sphere, 45 meters in diameter, on which were painted the constella...

---

### American Library in Paris
- **Coordinates**: (48.8589, 2.299)
- **Summary**: The American Library in Paris is the largest English-language lending library on the European mainland. It operates as an independent, non-profit cultural association in France incorporated under the laws of Delaware. Library members have access to more than 100,000 books and periodicals (of whic...

---

### Palazzo Bernardo Nani
- **Coordinates**: (48.8583, 2.2923)
![Palazzo Bernardo Nani](https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Palazzo_bernardo_nani_gran_canal_dorsoduro.jpg/250px-Palazzo_bernardo_nani_gran_canal_dorsoduro.jpg)
- **Summary**: The Palazzo Bernardo Nani Lucheschi, also called the Palazzo Nani Bernardo, is a Renaissance-style palace between the Palazzo Giustinian Bernardo and the larger and more grandiose Ca' Rezzonico, on the Grand Canal in the sestiere of Dorsoduro in Venice, Italy.

---

<!-- LIVE_RESULTS_END -->
