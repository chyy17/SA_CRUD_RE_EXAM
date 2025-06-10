from flask import Flask, render_template, request, redirect
from db import get_db_connection
import os
from flask import request, redirect
from werkzeug.utils import secure_filename
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

### ----------- Branch CRUD -----------
@app.route('/branches')
def branches():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Branch")
    branches = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('branches.html', branches=branches)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/add_branch', methods=['POST'])
def add_branch():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']

    logo_file = request.files.get('logo')
    logo_path = None

    if logo_file and logo_file.filename:
        filename = secure_filename(logo_file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Ensure directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        logo_file.save(save_path)

        # This path is used in <img src="{{ b.Logo }}">
        logo_path = '/' + save_path.replace('\\', '/')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Branch (Name, Email, Phone, Logo) VALUES (%s, %s, %s, %s)",
        (name, email, phone, logo_path)
    )
    db.commit()
    cursor.close()
    db.close()

    return redirect('/branches')

@app.route('/update_branch/<int:id>', methods=['POST'])
def update_branch(id):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']

    logo_file = request.files.get('logo')
    db = get_db_connection()
    cursor = db.cursor()

    if logo_file and logo_file.filename:
        filename = secure_filename(logo_file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        logo_file.save(save_path)
        logo_path = '/' + save_path.replace('\\', '/')

        cursor.execute("""
            UPDATE Branch
            SET Name=%s, Email=%s, Phone=%s, Logo=%s
            WHERE Id=%s
        """, (name, email, phone, logo_path, id))
    else:
        cursor.execute("""
            UPDATE Branch
            SET Name=%s, Email=%s, Phone=%s
            WHERE Id=%s
        """, (name, email, phone, id))

    db.commit()
    cursor.close()
    db.close()
    return redirect('/branches')


@app.route('/delete_branch/<int:id>')
def delete_branch(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Branch WHERE Id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/branches')

### ----------- Category CRUD -----------
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

@app.route('/update_category/<int:id>', methods=['POST'])
def update_category(id):
    name = request.form['name']
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE Category SET Name=%s WHERE Id=%s", (name, id))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/categories')

@app.route('/delete_category/<int:id>')
def delete_category(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Category WHERE Id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/categories')

### ----------- Product CRUD -----------
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

@app.route('/update_product/<int:id>', methods=['POST'])
def update_product(id):
    name = request.form['name']
    cost = request.form['cost']
    price = request.form['price']
    category_id = request.form['category']
    branch_id = request.form['branch']

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE Product
        SET Name=%s, Cost=%s, Price=%s, CategoryId=%s, BranchId=%s
        WHERE Id=%s
    """, (name, cost, price, category_id, branch_id, id))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/products')

@app.route('/delete_product/<int:id>')
def delete_product(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Product WHERE Id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/products')

if __name__ == '__main__':
    app.run(debug=True)
