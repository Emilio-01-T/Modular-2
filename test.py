import requests

BASE = "https://searx.tiekoetter.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def search(q):
    params = {
        "q": q,
        "format": "json",
        "language": "it",
        "engines": "google,bing"
    }
    response = requests.get(f"{BASE}/search", params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()

results = search("python openai")

for r in results.get("results", []):
    print(f"{r['title']} - {r['url']}")
