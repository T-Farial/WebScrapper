#pip install requests beautifulsoup4 pandas
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd


def fetch_page(url: str, timeout: int = 10) -> str | None:
    """Handles network requests, checking response status, timeouts, and wrong URLs."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        # Check for 200 OK status code
        response.raise_for_status()
        print(f"✅ Success: Received 200 status code from {url}")
        return response.text

    except requests.exceptions.Timeout:
        print(f"❌ Timeout Error: The request timed out after {timeout} seconds.")
    except requests.exceptions.HTTPError as err:
        print(f"❌ HTTP Error (e.g., 404/500): {err}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Unreachable website or invalid domain URL.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

    return None


def extract_data(html_content: str) -> list[dict]:
    """Extracts raw elements while gracefully handling structure changes or missing fields."""
    if not html_content:
        print("⚠️ Extraction skipped: No HTML content provided.")
        return []

    soup = BeautifulSoup(html_content, "html.parser")

    # Target element containers (Books to Scrape standard container)
    product_cards = soup.select(".product_pod")

    # Handle web structure change or missing root elements
    if not product_cards:
        print("⚠️ Structure Change Warning: No product elements matched the CSS selector.")
        return []

    extracted_records = []
    for card in product_cards:
        # Check if title exists
        title_el = card.select_one("h3 a")
        title = title_el.get("title") if title_el else None

        # Check if price element exists
        price_el = card.select_one(".price_color")
        price = price_el.get_text(strip=True) if price_el else None

        # Check if rating element exists
        rating_el = card.select_one(".star-rating")
        rating_classes = rating_el.get("class", []) if rating_el else []
        rating = next((cls for cls in rating_classes if cls != "star-rating"), None)

        extracted_records.append({
            "raw_title": title,
            "raw_price": price,
            "raw_rating": rating
        })

    print(f"✅ Extracted {len(extracted_records)} raw records.")
    return extracted_records


def clean_data(raw_records: list[dict]) -> pd.DataFrame:
    """Cleans strings, converts price to numeric float, maps ratings, drops duplicates and empties."""
    if not raw_records:
        return pd.DataFrame()

    df = pd.DataFrame(raw_records)

    # 1. Strip whitespace from string columns

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # 2. Extract & convert Price to float
    def parse_price(val):
        if not val or val == "None":
            return None
        match = re.search(r"[\d\.]+", str(val))
        return float(match.group()) if match else None

    df["price"] = df["raw_price"].apply(parse_price)

    # 3. Convert word ratings to numeric floats
    rating_map = {"One": 1.0, "Two": 2.0, "Three": 3.0, "Four": 4.0, "Five": 5.0}
    df["rating"] = df["raw_rating"].map(rating_map)

    # 4. Handle Empty Values (drop rows missing title or price)
    df.rename(columns={"raw_title": "title"}, inplace=True)
    df.dropna(subset=["title", "price"], inplace=True)

    # 5. Handle Duplicates
    initial_count = len(df)
    df.drop_duplicates(subset=["title"], keep="first", inplace=True)
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        print(f"🧹 Removed {duplicates_removed} duplicate records.")

    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Sanity checks: confirms price > 0, valid rating range, and non-empty titles."""
    if df.empty:
        return df

    # Data sanity rules
    valid_price = df["price"] > 0
    valid_rating = (df["rating"] >= 1.0) & (df["rating"] <= 5.0)
    valid_title = (df["title"] != "") & (df["title"] != "None")

    # Combine validation criteria
    is_valid = valid_price & valid_rating & valid_title

    invalid_rows = len(df) - is_valid.sum()
    if invalid_rows > 0:
        print(f"⚠️ Validation Warning: Dropped {invalid_rows} records failing sanity checks.")

    validated_df = df[is_valid][["title", "price", "rating"]].copy()
    print(f"✅ Data Validated: {len(validated_df)} records passed sanity checks.")
    return validated_df


def save_to_csv(df: pd.DataFrame, filename: str = "products.csv") -> bool:
    """Saves DataFrame to CSV and verifies creation, row count, and columns."""
    if df.empty:
        print("❌ CSV Export Failed: DataFrame is empty.")
        return False

    try:
        # Save to CSV
        df.to_csv(filename, index=False, encoding="utf-8")

        # Verification Checks
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            saved_df = pd.read_csv(filename)
            print(f"🎉 Verification Passed: '{filename}' created successfully.")
            print(f"   📊 Total Rows: {len(saved_df)} | Columns: {list(saved_df.columns)}")
            return True
        else:
            print("❌ Verification Failed: File does not exist or is empty.")
            return False

    except Exception as e:
        print(f"❌ File Save Exception: {e}")
        return False


def main():
    # Public sandbox URL for web scraping practice
    target_url = "http://books.toscrape.com/"

    

    print(f"🚀 Starting web scraper pipeline for: {target_url}\n")

    # Step 1: Fetch
    html = fetch_page(target_url)
    if not html:
        print("Pipeline aborted due to network/fetch failure.")
        return

    # Step 2: Extract
    raw_data = extract_data(html)

    # Step 3: Clean
    cleaned_df = clean_data(raw_data)

    # Step 4: Validate
    validated_df = validate_data(cleaned_df)

    # Step 5: Save & Verify
    save_to_csv(validated_df, filename="scraped_books.csv")

# Test validate_data with invalid values
test_validation = pd.DataFrame([
    {"title": "Valid Book", "price": 20.0, "rating": 5.0},
    {"title": "Free Book", "price": 0.0, "rating": 4.0},
    {"title": "Bad Rating", "price": 30.0, "rating": 6.0},
    {"title": "", "price": 25.0, "rating": 3.0},
])

print("\n--- Testing Data Validation ---")
validated_test = validate_data(test_validation)

print(validated_test)

if __name__ == "__main__":
    main()