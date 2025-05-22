from flask import Flask, render_template, request, redirect, url_for
from models import SuperMarket, Product

app = Flask(__name__)
supermarket = SuperMarket()

@app.route('/')
def index():
    all_products = supermarket.list_products()
    products = [p for p in all_products if p[3] == 1]  # Kun varer i kurv

    total_stock = sum(p[2] for p in products)
    total_price = sum(p[1] * p[2] for p in products)  # Pris * antal for hvert produkt

    # Hent alle produktnavne til dropdown
    dropdown_options = supermarket.list_all_available_products()

    return render_template(
        'index.html',
        products=products,
        total_stock=total_stock,
        total_price=total_price,
        dropdown_options=dropdown_options
    )


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
    product_data = supermarket.search_product(name)
    if product_data:
        current = product_data[0]
        # Sæt quantity til 0 og in_cart til 0
        supermarket.cursor.execute(
            "UPDATE supermarket SET quantity = 0, in_cart = 0 WHERE name = ?", (name,)
        )
        supermarket.conn.commit()
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
    quantity = int(request.form['quantity'])

    # Find produkt og markér som "i kurven"
    product_data = supermarket.search_product(name)
    if product_data:
        supermarket.add_to_cart(name, quantity)
    
    return redirect(url_for('index'))

@app.route('/checkout')
def checkout():
    all_products = supermarket.list_products()
    products = [p for p in all_products if p[3] == 1]  # Kun produkter i kurven
    total_price = sum(p[1] * p[2] for p in products)

    return render_template('checkout.html', products=products, total_price=total_price)

@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    # Tøm kurven ved at sætte in_cart = 0
    supermarket.cursor.execute("UPDATE supermarket SET in_cart = 0 WHERE in_cart = 1")
    supermarket.conn.commit()

    return "<h1>Tak for din betaling! ✅</h1><p><a href='/'>Tilbage til forsiden</a></p>"

if __name__ == '__main__':
    app.run(debug=True)
