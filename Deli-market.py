from flask import Flask, render_template, request, redirect, url_for, flash
from models import SuperMarket, Product

app = Flask(__name__)
supermarket = SuperMarket()

@app.route('/')
def index():
    all_products = supermarket.list_products()
    products = [p for p in all_products if p[3] == 1]  # produkter i kurven

    total_stock = sum(p[4] for p in products)  # cart_quantity
    total_price = sum(p[1] * p[4] for p in products)  # pris * cart_quantity

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
    total_price = sum(product[1] * product[2] for product in results)

    
    dropdown_options = supermarket.list_all_available_products()

    return render_template(
        'index.html',
        products=results,
        total_stock=total_stock,
        total_price=total_price,
        dropdown_options=dropdown_options
    )

@app.route('/reduce')
def reduce():
    products = supermarket.list_products()
    total_stock = sum(product[2] for product in products)
    return render_template('index.html', products=products, total_stock=total_stock)

@app.route('/delete/<name>', methods=['POST'])
def delete_product(name):
    referer = request.referrer or ''
    
    if '/lager' in referer:
       
        return "Sletning ikke tilladt fra lager-siden", 403
    else:
       
        supermarket.cursor.execute(
            "UPDATE supermarket SET in_cart = 0 WHERE name = ?", (name,)
        )
        supermarket.conn.commit()
        return redirect(url_for('index'))

@app.route('/edit/<name>', methods=['GET', 'POST'])
def edit_product(name):
    from_lager = request.args.get('from') == 'lager'

    if request.method == 'POST':
        price = float(request.form['price']) 
        quantity = int(request.form['quantity'])

        existing_product = supermarket.search_product(name)[0]
        in_cart = existing_product[3]

       
        if from_lager:
            supermarket.cursor.execute(
                "UPDATE supermarket SET price = ?, quantity = ? WHERE name = ?",
                (price, quantity, name)
            )
        else:
            supermarket.cursor.execute(
                "UPDATE supermarket SET quantity = ? WHERE name = ?",
                (quantity, name)
            )

        supermarket.conn.commit()

        
        if from_lager:
            return redirect(url_for('lager'))
        else:
            return redirect(url_for('index'))

    else:
        product_data = supermarket.search_product(name)
        if product_data:
            product = product_data[0]  
            return render_template('edit.html', product=product, from_lager=from_lager)
        else:
            return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_product():
    name = request.form['name']
    quantity = int(request.form['quantity'])

    product_data = supermarket.search_product(name)
    if product_data:
        current_stock = product_data[0][2]
        if quantity <= current_stock:
            supermarket.add_to_cart(name, quantity)
         
            updated_product_data = supermarket.search_product(name)
            updated_stock = updated_product_data[0][2]

        
            return redirect(url_for('index'))
        else:
            return f"<h3>🚫 Ikke nok på lager til '{name}'. Kun {current_stock} stk. tilgængelige.</h3><a href='/'>⬅️ Tilbage</a>", 400
    
    return redirect(url_for('index'))


@app.route('/add_to_inventory', methods=['POST'])
def add_to_inventory():
    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    new_product = Product(name, price, quantity)
    supermarket.add_product(new_product)
    return redirect(url_for('lager'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/checkout')
def checkout():
    all_products = supermarket.list_products()
    products = [p for p in all_products if p[3] == 1]  
    total_price = sum(p[1] * p[4] for p in products)  

    return render_template('checkout.html', products=products, total_price=total_price)


@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    supermarket.cursor.execute(
        "UPDATE supermarket SET in_cart = 0, cart_quantity = 0 WHERE in_cart = 1"
    )
    supermarket.conn.commit()
    return "<h1>Tak for din betaling! ✅</h1><p><a href='/'>Tilbage til forsiden</a></p>"

@app.route('/lager')
def lager():
    products = supermarket.list_products()
    return render_template('lager.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
