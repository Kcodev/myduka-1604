from flask import Flask, redirect, render_template, request, url_for, flash
from datetime import datetime
import psycopg2

app = Flask(__name__)
app.secret_key = 'This is a secreat key'


# conn = psycopg2.connect(database="myduka", user="postgres",
#                         password='12345', port='5432', host='localhost')
conn = psycopg2.connect(database="dcj4jr81570svg", user="mkkdzfgnoessvj",
                        password='2cbb7bf2eaa0d0a16ac576e7afd6f9c88cc9e27128598a4cff21a43e4b31a969', port='5432', host='ec2-34-253-119-24.eu-west-1.compute.amazonaws.com')

cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS products(id serial PRIMARY KEY, name VARCHAR ( 100 ) NOT NULL,buying_price NUMERIC(14, 2), selling_price NUMERIC(14, 2), stock_quantity INT DEFAULT 0);")

cur.execute("CREATE TABLE IF NOT EXISTS sales(id serial PRIMARY KEY, pid int, quantity numeric(5,2), created_at TIMESTAMP, CONSTRAINT myproduct FOREIGN KEY(pid) references products(id) on UPDATE cascade on DELETE restrict);")

conn.commit()


@app.route('/')
@app.route('/Home')
def home():
    return render_template('index.html')


# inventories route
@app.route('/inventorie')
def inventories():
    cur.execute("SELECT * FROM products ORDER BY id;")
    records = cur.fetchall()

    return render_template('inventorie.html', records=records)


# View Indivitual product
@app.route('/inventorie/<int:x>')
def view_item(x):
    cur.execute("select * from products where id=%(id)s;", {"id": x})

    x = cur.fetchall()

    print(x)
    return render_template("inventorie.html", records=x)


# sales route
@app.route('/sales')
def sales():
    cur.execute("SELECT * FROM sales ORDER BY created_at;")

    sales = cur.fetchall()

    cur.execute("SELECT count(id) FROM sales;")

    p = str(cur.fetchall())

    return render_template('sales.html', sale=sales, p=p)

# view sale


@app.route('/sales/<int:x>')
def view_sales(x):
    # query the sales for that product_id
    cur.execute("SELECT * FROM sales WHERE id=%(id)s;", {"id": x})
    x = cur.fetchall()
    return render_template("sales.html", sale=x)

# adding ptoduct route


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['p_name']
        bp = request.form['bp']
        sp = request.form['sp']
        quantity = request.form['quantity']

        cur.execute("SELECT name from products;")
        x = cur.fetchall()
        print(x)

        cur.execute("INSERT INTO products (name, buying_price, selling_price, stock_quantity) VALUES (%s, %s, %s, %s)",
                    (name, bp, sp, quantity))

        conn.commit()
        flash('You have added a new product', 'info')
        return redirect('/inventorie')
    else:
        return redirect('/inventorie')


# Making sales route
@app.route('/make_sale', methods=['GET', 'POST'])
def make_sale():
    if request.method == "POST":
        pid = request.form['pid']
        quantity = request.form['qty']
        created_at = datetime.now()
        # # # from datetime import datetime
        cur.execute(
            "UPDATE products SET stock_quantity=(stock_quantity-%s) WHERE id=%s;", (quantity, pid))

        cur.execute("INSERT INTO sales (pid, quantity, created_at) VALUES (%s, %s, %s)",
                    (pid, quantity, created_at))

        conn.commit()

        return redirect('/inventorie')


# search route
@app.route('/search', methods=["GET", "POST"])
def search():
    id_serch = request.form['search']

    # cur.execute("SELECT name FROM products where id = %s", id_serch)
    cur.execute(
        "SELECT id,pid,quantity, created_at FROM sales where pid =%s", id_serch)
    name_s = cur.fetchall()

    cur.execute("SELECT name FROM products where id=%s", id_serch)
    pr = cur.fetchall()

    return render_template("search.html", name_s=name_s, pp=pr)


@app.context_processor
def utility_processor():
    def count_products():
        cur.execute("SELECT count(name) FROM products;")
        num = cur.fetchone()
        return num
    return dict(count_products=count_products)


# Count Update
@app.context_processor
def utility_processor():
    def count_sales():
        cur.execute("SELECT count(pid) FROM sales;")
        num = cur.fetchone()
        return num
    return dict(count_sales=count_sales)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':
        # fetch from forms
        pid = int(request.form['pid'])
        print(type(int(pid)))
        name = request.form['p_name']
        bp = request.form['bp']
        sp = request.form['sp']
        quantity = request.form['quantity']

        cur.execute(
            "SELECT name FROM products where id= %s;", pid)
        names = cur.fetchone()
        print(names)
        cur.execute(
            "SELECT buying_price FROM products where id= %s", pid)
        buy = cur.fetchone()
        cur.execute(
            "SELECT selling_price FROM products where id= %s", pid)
        sell = cur.fetchone()
        cur.execute(
            "SELECT stock_quantity FROM products where id= %s", pid)
        stock = cur.fetchone()

        print(type(pid))

        if names != name or buy != bp or sell != sp or quantity != stock:
            cur.execute(
                "UPDATE products SET name=(%s) WHERE id=%s;", (name, pid))
            cur.execute(
                "UPDATE products SET buying_price =(%s) WHERE id=%s;", (bp, pid))
            cur.execute(
                "UPDATE products SET selling_price =(%s) WHERE id=%s;", (sp, pid))
            cur.execute(
                "UPDATE products SET stock_quantity =(%s) WHERE id=%s;", (quantity, pid))
            conn.commit()

            return redirect('/inventorie', id)
    else:
        return 'Error in redirecting'


@app.route("/dashboard")
def dashboard():
    cur.execute("SELECT name, stock_quantity FROM products;")
    data = cur.fetchall()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    cur.execute(
        "SELECT products.name, cast(quantity as integer) FROM sales join products on sales.pid=products.id;")
    sales = cur.fetchall()

    label_x = [row[0] for row in sales]
    value_y = [row[1] for row in sales]

    return render_template('dashboard.html', labels=labels, values=values, label_x=label_x, value_y=value_y)


if __name__ == "__main__":
    app.run(debug=True)
