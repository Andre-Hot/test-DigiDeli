from flask import Flask, render_template, request, redirect, url_for
from models import SuperMarket, Product

app = Flask(__name__)
supermarket = SuperMarket()

@app.route('/')
def index():
    products = supermarket.list_products()
    return render_template('index.html', products=products)

@app.route('/add', methods=['POST'])
def add_product():
    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])
    new_product = Product(name, price, quantity)
    supermarket.add_product(new_product)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
