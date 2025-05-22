from flask import Flask, render_template, request, redirect, url_for
from models import SuperMarket, Product

app = Flask(__name__)
supermarket = SuperMarket()

@app.route('/')
def index():
    products = supermarket.list_products()
    total_stock = sum(product[2] for product in products)
    return render_template('index.html', products=products, total_stock=total_stock)

@app.route('/search')
def search():
    query = request.args.get('query')
    results = supermarket.search_product(query)
    total_stock = sum(product[2] for product in results)
    return render_template('index.html', products=results, total_stock=total_stock)

@app.route('/reduce')
def reduce():
    products = supermarket.list_products()
    total_stock = sum(product[2] for product in products)
    return render_template('index.html', products=products, total_stock=total_stock)

@app.route('/delete/<name>', methods=['POST'])
def delete_product(name):
    supermarket.remove_product(name)
    return redirect(url_for('index'))

@app.route('/edit/<name>', methods=['GET', 'POST'])
def edit_product(name):
    if request.method == 'POST':
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        updated_product = Product(name, price, quantity)
        supermarket.update_product(updated_product)
        return redirect(url_for('index'))
    else:
        product_data = supermarket.search_product(name)
        if product_data:
            product = product_data[0]  # (name, price, quantity)
            return render_template('edit.html', product=product)
        else:
            return redirect(url_for('index'))

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
