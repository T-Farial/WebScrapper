# Web Scraper & Data Cleaner

A Python web-scraping application that collects book data from a public practice website, cleans and validates the results, and exports the final dataset to CSV.

## What It Does

The application follows a simple data-processing pipeline:

**Fetch → Extract → Clean → Validate → Save**

It:

* Fetches webpage content using `requests`
* Parses HTML using BeautifulSoup
* Extracts book titles, prices, and ratings
* Converts raw prices and ratings into usable numeric values
* Removes incomplete and duplicate records
* Validates the cleaned data
* Exports the final dataset to CSV
* Verifies that the CSV was created successfully

## Technologies

* Python
* Requests
* BeautifulSoup
* Pandas
* Regular Expressions
* CSV / File Handling

## Data Source

The project uses [Books to Scrape](https://books.toscrape.com/), a public website specifically designed for practicing web scraping.

## Error Handling

The application includes handling for:

* Invalid or unreachable URLs
* Connection failures
* Request timeouts
* HTTP errors
* Unexpected webpage structures
* Missing data
* Invalid prices
* Invalid ratings
* Empty datasets
* CSV export failures

The program is designed to fail gracefully rather than producing an unhandled traceback.

## Data Cleaning

Raw scraped data is transformed into a structured dataset.

Examples include:

* `"£51.77"` → `51.77`
* `"Five"` → `5.0`
* Missing titles or prices → removed
* Duplicate book titles → removed
* Invalid prices or ratings → rejected during validation

## Output

The program produces:

```text
scraped_books.csv
```

with the following columns:

```text
title
price
rating
```

The current test run successfully extracted and validated **20 records**.

## Example

Example output:

| title                | price | rating |
| -------------------- | ----: | -----: |
| A Light in the Attic | 51.77 |      3 |
| Tipping the Velvet   | 53.74 |      1 |
| Soumission           | 50.10 |      1 |
| Sharp Objects        | 47.82 |      4 |

## How to Run

Install the required libraries:

```bash
pip install requests beautifulsoup4 pandas
```

Run the program:

```bash
python DataCWebS.py
```

The program will fetch the data, process it, validate it, and create `scraped_books.csv`.

## Testing

The application was tested for:

* Successful scraping
* HTTP 200 responses
* Invalid URLs
* Connection failures
* Unexpected webpage structures
* Missing and invalid data
* Invalid validation values
* CSV creation and verification

## Skills Demonstrated

This project demonstrates practical experience with:

* Python programming
* Web scraping
* HTML parsing
* Data cleaning
* Data validation
* Pandas DataFrames
* Exception handling
* File and CSV processing
* Building a modular data pipeline
