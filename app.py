from flask import Flask, render_template, request, redirect
from db import get_db_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

### Branch CRUD
@app.route('/branches')
def branches():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Branch")
    branches = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('branches.html', branches=branches)

@app.route('/add_branch', methods=['POST'])
def add_branch():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    logo = request.form['logo']
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Branch (Name, Email, Phone, Logo) VALUES (%s, %s, %s, %s)",
                   (name, email, phone, logo))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/branches')

### Category CRUD
@app.route('/categories')
def categories():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Category")
    categories = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['name']
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Category (Name) VALUES (%s)", (name,))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/categories')

### Product CRUD
@app.route('/products')
def products():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Category")
    categories = cursor.fetchall()

    cursor.execute("SELECT * FROM Branch")
    branches = cursor.fetchall()

    cursor.execute("""
        SELECT p.*, c.Name AS CategoryName, b.Name AS BranchName
        FROM Product p
        JOIN Category c ON p.CategoryId = c.Id
        JOIN Branch b ON p.BranchId = b.Id
    """)
    products = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('products.html', products=products, categories=categories, branches=branches)

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    cost = request.form['cost']
    price = request.form['price']
    category_id = request.form['category']
    branch_id = request.form['branch']

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO Product (Name, Cost, Price, CategoryId, BranchId)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, cost, price, category_id, branch_id))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/products')

if __name__ == '__main__':
    app.run(debug=True)
