import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")

BASE = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE, "narrationOutput.json")
OUTPUT_FILE = os.path.join(BASE, "revisedNarrationOutput.json")

GENERAL_PREFIX = "image of"

def build_google_query(keyword):
    return f"{GENERAL_PREFIX} {keyword}"

async def google_image_search(session, query):
    if not query:
        return ""

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "searchType": "image",
        "q": query,
        "num": 1
    }

    try:
        async with session.get(url, params=params, timeout=25) as res:
            text = await res.text()
            if res.status != 200:
                return ""
            data = json.loads(text)
            items = data.get("items")
            if not items:
                return ""
            return items[0].get("link", "")
    except:
        return ""

async def main():
    with open(INPUT_FILE) as f:
        data = json.load(f)

    items = data["results"]

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        for item in items:
            keywords = item.get("images", [])
            queries = [build_google_query(k) for k in keywords]
            tasks = [google_image_search(session, q) for q in queries]
            urls = await asyncio.gather(*tasks)

            item["images"] = [
                {"query": q, "url": u or ""}
                for q, u in zip(queries, urls)
            ]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print("✔ Saved:", OUTPUT_FILE)

if __name__ == "__main__":
    asyncio.run(main())
