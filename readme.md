# Steam Market Web Scraper API

This project is a web scraper designed to extract buy and sell prices from the Steam Market, specifically for items listed under `appid=730` (CS:GO). It uses **Selenium** for web scraping, **Flask** for the API, and stores the scraped data in an **SQLite** database. The entire setup is Dockerized for easy deployment and use.

## Features

- Scrapes buy and sell prices for items listed on the Steam Market.
- Extracts recent activity for each item.
- Supports pagination for multiple pages.
- Uses a rotating proxy service for IP rotation (ScraperAPI).
- Exposes the scraping functionality through a **Flask API**.
- Stores the scraped data in **SQLite**.
- Containerized with **Docker** for easy setup and deployment.

## Prerequisites

- **Docker** and **Docker Compose** installed on your system.
- A **ScraperAPI key** for rotating IPs during scraping.
- [Google Chrome](https://www.google.com/chrome/) and [ChromeDriver](https://sites.google.com/chromium.org/driver/) are used by Selenium to perform web scraping.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/steam-market-scraper.git
cd steam-market-scraper

ENV:
SCRAPER_API_KEY=your_scraperapi_key
SCRAPER_URL=https://steamcommunity.com/market/search?appid=730
SCRAPER_MAX_PAGES=5

Build Docker:
docker build -t web_scraper_image .

Run Docker:
docker run -d -p 5000:5000 web_scraper_image

Check the API is Running
curl http://localhost:5000/

Start a Scraping Session:
curl -X POST http://localhost:5000/scrape -H "Content-Type: application/json" -d '{"url": "https://steamcommunity.com/market/search?appid=730", "max_pages": 5}'

Get Scraped Products:
curl http://localhost:5000/products

Get a Specific Product by URL:
curl http://localhost:5000/products/{product_url}

