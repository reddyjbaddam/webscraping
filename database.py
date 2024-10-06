import sqlite3

# SQLite setup
def create_database():
    conn = sqlite3.connect('steam_marketplace.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            buy_price TEXT,
            buy_quantity TEXT,
            sell_price TEXT,
            sell_quantity TEXT,
            recent_activity TEXT
        )
    ''')

    conn.commit()
    conn.close()


def save_to_database(product_data):
    conn = sqlite3.connect('steam_marketplace.db')
    cursor = conn.cursor()

    for product in product_data:
        cursor.execute('''
            INSERT INTO products (buy_price,buy_quantity, sell_price, sell_quantity, url,recent_activity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
        product['url'], product['buy_price'], product['buy_quantity'], product['sell_price'], product['sell_quantity'],
        product['recent_activity']))

    conn.commit()
    conn.close()

