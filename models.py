import sqlite3

class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f"Product Name: {self.name}\nPrice: {self.price}\nQuantity: {self.quantity}"

class SuperMarket:
    def __init__(self, db_name='supermarket.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        query = "CREATE TABLE IF NOT EXISTS supermarket (name TEXT PRIMARY KEY, price FLOAT, quantity INT)"
        self.cursor.execute(query)
        self.conn.commit()

    def add_product(self, product):
        query = "INSERT OR REPLACE INTO supermarket (name, price, quantity) VALUES (?, ?, ?)"
        self.cursor.execute(query, (product.name, product.price, product.quantity))
        self.conn.commit()

    def remove_product(self, name):
        query = "DELETE FROM supermarket WHERE name = ?"
        self.cursor.execute(query, (name,))
        self.conn.commit()

    def list_products(self):
        query = "SELECT * FROM supermarket"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_product(self, product):
        query = "UPDATE supermarket SET price = ?, quantity = ? WHERE name = ?"
        self.cursor.execute(query, (product.price, product.quantity, product.name))
        self.conn.commit()

    def search_product(self, name):
        query = "SELECT * FROM supermarket WHERE LOWER(name) LIKE ?"
        self.cursor.execute(query, (f"%{name.lower()}%",))
        return self.cursor.fetchall()

    def filter_products(self, min_price, max_price):
        query = "SELECT * FROM supermarket WHERE price BETWEEN ? AND ?"
        self.cursor.execute(query, (min_price, max_price))
        return self.cursor.fetchall()
