import os
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from db import get_db_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def _is_allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def _save_logo(logo_file):
    if not logo_file or not logo_file.filename:
        return None
    if not _is_allowed_image(logo_file.filename):
        raise ValueError("Only PNG, JPG, JPEG, GIF, and WEBP images are allowed.")

    filename = secure_filename(logo_file.filename)
    save_path = UPLOAD_FOLDER / filename
    logo_file.save(save_path)
    return url_for("static", filename=f"uploads/{filename}")


@app.before_request
def ensure_database():
    if not getattr(app, "_database_initialized", False):
        initialize_database()
        app._database_initialized = True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/branches")
def branches():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Branch ORDER BY Id DESC")
        branch_rows = cursor.fetchall()
    finally:
        cursor.close()
        db.close()
    return render_template("branches.html", branches=branch_rows)


@app.route("/add_branch", methods=["POST"])
def add_branch():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    if not name or not email or not phone:
        return redirect(url_for("branches"))

    try:
        logo_path = _save_logo(request.files.get("logo"))
    except ValueError:
        return redirect(url_for("branches"))

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Branch (Name, Email, Phone, Logo) VALUES (%s, %s, %s, %s)",
            (name, email, phone, logo_path),
        )
        db.commit()
    finally:
        cursor.close()
        db.close()
    return redirect(url_for("branches"))


@app.route("/update_branch/<int:id>", methods=["POST"])
def update_branch(id):
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    if not name or not email or not phone:
        return redirect(url_for("branches"))

    logo_file = request.files.get("logo")
    db = get_db_connection()
    cursor = db.cursor()
    try:
        if logo_file and logo_file.filename:
            logo_path = _save_logo(logo_file)
            cursor.execute(
                "UPDATE Branch SET Name=%s, Email=%s, Phone=%s, Logo=%s WHERE Id=%s",
                (name, email, phone, logo_path, id),
            )
        else:
            cursor.execute(
                "UPDATE Branch SET Name=%s, Email=%s, Phone=%s WHERE Id=%s",
                (name, email, phone, id),
            )
        db.commit()
    except ValueError:
        db.rollback()
    finally:
        cursor.close()
        db.close()
    return redirect(url_for("branches"))


@app.route("/delete_branch/<int:id>", methods=["POST"])
def delete_branch(id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Branch WHERE Id=%s", (id,))
        db.commit()
    finally:
        cursor.close()
        db.close()
    return redirect(url_for("branches"))


@app.route("/categories")
def categories():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Category ORDER BY Id DESC")
        category_rows = cursor.fetchall()
    finally:
        cursor.close()
        db.close()
    return render_template("categories.html", categories=category_rows)


@app.route("/add_category", methods=["POST"])
def add_category():
    name = request.form.get("name", "").strip()
    if name:
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO Category (Name) VALUES (%s)", (name,))
            db.commit()
        finally:
            cursor.close()
            db.close()
    return redirect(url_for("categories"))


@app.route("/update_category/<int:id>", methods=["POST"])
def update_category(id):
    name = request.form.get("name", "").strip()
    if name:
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE Category SET Name=%s WHERE Id=%s", (name, id))
            db.commit()
        finally:
            cursor.close()
            db.close()
    return redirect(url_for("categories"))


@app.route("/delete_category/<int:id>", methods=["POST"])
def delete_category(id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Category WHERE Id=%s", (id,))
        db.commit()
    finally:
        cursor.close()
        db.close()
    return redirect(url_for("categories"))


@app.route("/products")
def products():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Category ORDER BY Name")
        category_rows = cursor.fetchall()

        cursor.execute("SELECT * FROM Branch ORDER BY Name")
        branch_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT p.*, c.Name AS CategoryName, b.Name AS BranchName
            FROM Product p
            JOIN Category c ON p.CategoryId = c.Id
            JOIN Branch b ON p.BranchId = b.Id
            ORDER BY p.Id DESC
            """
        )
        product_rows = cursor.fetchall()
    finally:
        cursor.close()
        db.close()
    return render_template(
        "products.html",
        products=product_rows,
        categories=category_rows,
        branches=branch_rows,
    )


def _product_form_values():
    name = request.form.get("name", "").strip()
    cost = request.form.get("cost", "").strip()
    price = request.form.get("price", "").strip()
    category_id = request.form.get("category", "").strip()
    branch_id = request.form.get("branch", "").strip()
    if not all([name, cost, price, category_id, branch_id]):
        raise ValueError("All product fields are required.")
    float(cost)
    float(price)
    return name, cost, price, int(category_id), int(branch_id)


@app.route("/add_product", methods=["POST"])
def add_product():
    try:
        values = _product_form_values()
    except (ValueError, TypeError):
        return redirect(url_for("products"))

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Product (Name, Cost, Price, CategoryId, BranchId)
            VALUES (%s, %s, %s, %s, %s)
            """,
            values,
        )
        db.commit()
    finally:
        cursor.close()
        db.close()
    return redirect(url_for("products"))


@app.route("/update_product/<int:id>", methods=["POST"])
def update_product(id):
    try:
        name, cost, price, category_id, branch_id = _product_form_values()
    except (ValueError, TypeError):
        return redirect(url_for("products"))

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            UPDATE Product
            SET Name=%s, Cost=%s, Price=%s, CategoryId=%s, BranchId=%s
            WHERE Id=%s
            """,
            (name, cost, price, category_id, branch_id, id),
        )
        db.commit()
    finally:
        cursor.close()
        db.close()
    return redirect(url_for("products"))


@app.route("/delete_product/<int:id>", methods=["POST"])
def delete_product(id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Product WHERE Id=%s", (id,))
        db.commit()
    finally:
        cursor.close()
        db.close()
    return redirect(url_for("products"))


@app.errorhandler(413)
def request_too_large(_error):
    return "Uploaded file is too large. Maximum size is 5 MB.", 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
