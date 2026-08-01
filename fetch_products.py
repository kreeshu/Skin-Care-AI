import requests
import csv
import time

BASE_URL = "https://www.api.foreveryng.com/api/V2/filter?category=3&page={}"
PAGES = 38
OUTPUT_FILE = "products.csv"

HEADERS = [
    "id", "name", "slug", "coverImage", "type",
    "stockQuantity", "price", "discountedPrice",
    "isDiscounted", "discountPercent", "isBestSeller",
    "review_count", "rating"
]

all_products = []

for page in range(1, PAGES + 1):
    url = BASE_URL.format(page)
    print(f"Fetching page {page}/{PAGES}...")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("data", {}).get("products", [])
        for p in products:
            rating_data = p.get("ratingAndReview", {})
            row = {
                "id": p.get("id"),
                "name": p.get("name"),
                "slug": p.get("slug"),
                "coverImage": p.get("coverImage"),
                "type": p.get("type"),
                "stockQuantity": p.get("stockQuantity"),
                "price": p.get("price"),
                "discountedPrice": p.get("discountedPrice"),
                "isDiscounted": p.get("isDiscounted"),
                "discountPercent": p.get("discountPercent"),
                "isBestSeller": p.get("isBestSeller"),
                "review_count": rating_data.get("total"),
                "rating": rating_data.get("averageRating"),
            }
            all_products.append(row)
        print(f"  -> Got {len(products)} products (total: {len(all_products)})")
    except Exception as e:
        print(f"  -> ERROR on page {page}: {e}")
    time.sleep(0.5)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=HEADERS)
    writer.writeheader()
    writer.writerows(all_products)

print(f"\nDone! {len(all_products)} products saved to {OUTPUT_FILE}")
