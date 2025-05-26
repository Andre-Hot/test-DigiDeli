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
        query = """
        CREATE TABLE IF NOT EXISTS supermarket (
            name TEXT PRIMARY KEY,
            price FLOAT,
            quantity INT,
            in_cart BOOLEAN DEFAULT 0,
            cart_quantity INT DEFAULT 0
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def add_product(self, product):
        query = """
        INSERT OR REPLACE INTO supermarket (name, price, quantity, in_cart, cart_quantity) 
        VALUES (?, ?, ?, 0, 0)
        """
        self.cursor.execute(query, (product.name, product.price, product.quantity))
        self.conn.commit()

    def remove_product(self, name):
        query = "DELETE FROM supermarket WHERE name = ?"
        self.cursor.execute(query, (name,))
        self.conn.commit()

    def list_products(self):
        self.cursor.execute("SELECT name, price, quantity, in_cart, cart_quantity FROM supermarket")
        return self.cursor.fetchall()

    def update_product(self, product):
        query = "UPDATE supermarket SET price = ?, quantity = ? WHERE name = ?"
        self.cursor.execute(query, (product.price, product.quantity, product.name))
        self.conn.commit()

    def search_product(self, name):
        query = "SELECT name, price, quantity, in_cart, cart_quantity FROM supermarket WHERE LOWER(name) LIKE ?"
        self.cursor.execute(query, (f"%{name.lower()}%",))
        return self.cursor.fetchall()

    def filter_products(self, min_price, max_price):
        query = "SELECT name, price, quantity, in_cart, cart_quantity FROM supermarket WHERE price BETWEEN ? AND ?"
        self.cursor.execute(query, (min_price, max_price))
        return self.cursor.fetchall()
    
    def add_to_cart(self, name, quantity):
        self.cursor.execute("SELECT quantity, cart_quantity FROM supermarket WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        if not result:
            raise ValueError("Produkt ikke fundet")

        current_stock, current_cart_qty = result

        if quantity > current_stock:
            raise ValueError("Ikke nok på lager")

        new_stock = current_stock - quantity
        new_cart_qty = current_cart_qty + quantity

        self.cursor.execute(
            "UPDATE supermarket SET quantity = ?, cart_quantity = ?, in_cart = 1 WHERE name = ?",
            (new_stock, new_cart_qty, name)
        )
        self.conn.commit()

    def list_all_available_products(self):
        query = "SELECT name FROM supermarket"
        self.cursor.execute(query)
        return self.cursor.fetchall()
