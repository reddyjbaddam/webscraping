import os
import json
import sqlite3
from flask import Flask, jsonify, request

# Import your existing scraping functions
from scraper import create_database, get_driver, scrape_item_prices, get_product_links, save_to_database

app = Flask(__name__)

# Database path
DATABASE = 'steam_marketplace.db'

# Initialize the database
create_database()

# Function to query data from the SQLite database
def query_database(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return (rows[0] if rows else None) if one else rows

# Home endpoint
@app.route('/')
def home():
    return jsonify({"message": "Steam Market Scraper API is running."})

# Scrape endpoint to start the scraping process
@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    max_pages = int(request.json.get('max_pages', 10))

    driver = get_driver()
    try:
        driver.get(url)
        current_page = 1

        while current_page <= max_pages:
            print(f"Scraping page {current_page}...")

            product_links = get_product_links(driver, max_items=10)
            for product_link in product_links:
                driver.execute_script(f"window.open('{product_link}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

                product_data = scrape_item_prices(driver, product_link)
                save_to_database(product_data)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            # You can add the next page button click logic if applicable
            current_page += 1

        return jsonify({"status": "success", "message": "Scraping completed"})
    finally:
        driver.quit()

# Endpoint to get all scraped products from the database
@app.route('/products', methods=['GET'])
def get_products():
    products = query_database('SELECT * FROM product_data')
    return jsonify([dict(row) for row in products])

# Endpoint to get a specific product by URL
@app.route('/products/<path:url>', methods=['GET'])
def get_product_by_url(url):
    product = query_database('SELECT * FROM product_data WHERE url = ?', [url], one=True)
    if product:
        return jsonify(dict(product))
    return jsonify({"error": "Product not found"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
