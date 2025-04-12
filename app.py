import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta

from helpers import apology, login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///inventory.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show Dashboard"""
    product_count = db.execute("SELECT COUNT(*) AS product_count FROM products")[0]["product_count"] or 0
    category_count = db.execute("SELECT COUNT(*) AS category_count FROM categories")[0]["category_count"] or 0
    total_sales = db.execute("SELECT SUM(sales.sale_amount) AS total_sales FROM sales")[0]["total_sales"] or 0
    total_purchases = db.execute("SELECT SUM(purchases.purchase_amount) AS total_purchases FROM purchases")[0]["total_purchases"] or 0
    total_expenses = db.execute("SELECT SUM(other_expenses.expense_amount) AS total_expenses FROM other_expenses")[0]["total_expenses"] or 0
    profit_loss = total_sales - (total_purchases + total_expenses)
    Out_of_stock = "Out of Stock"
    stockouts = db.execute("SELECT COUNT(*) AS stockouts FROM products WHERE stock_status = ?", Out_of_stock)[0]["stockouts"] or 0
    return render_template("index.html", product_count=product_count, category_count=category_count, total_sales=total_sales, total_purchases=total_purchases, total_expenses=total_expenses, profit_loss=profit_loss, stockouts=stockouts)
    
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        
        # Ensure the correct role has been input
        if request.form.get("role") != rows[0]["role"]:
            return apology("Please select the correct role")

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        print(session["user_id"])
        print(session["username"])

        # Save role in session
        session["role"] = rows[0]["role"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        role = request.form.get("role")

        if not username:
            return apology("Please provide a Username!")
        elif not password:
            return apology("Please provide a Password!")
        elif not confirm:
            return apology("Please confirm Password!")
        elif not role:
            return apology("Please select a role")

        if password != confirm:
            return apology("Passwords do not match!")

        hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, hash, role) VALUES (?, ?, ?)", username, hash, role)
            return redirect("/")
        except:
            return apology("Username has already been registered!")
    else:
        return render_template("register.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/sales")
@login_required
def sales():
    sales = db.execute("SELECT sales.id, sales.product_id, sales.date AS sale_date, sales.quantity, sales.sale_price, sales.sale_amount, sales.qty_after_sale, products.product_name FROM sales JOIN products ON sales.product_id = products.id ORDER BY sale_date DESC")
    for sale in sales:
        sale["sale_date_raw"] = sale["sale_date"] # Pick the original date to allow for proper comparison when filtering
        sale["sale_date"] = datetime.strptime(sale["sale_date"], "%Y-%m-%d").strftime("%a, %d %b %Y")
    total_sales = db.execute("SELECT SUM(sales.sale_amount) AS total_sales FROM sales")[0]["total_sales"] or 0
    return render_template("sales.html", sales=sales, total_sales=total_sales, table_id="salesTable")


@app.route("/purchases")
@login_required
def purchases():
    purchases = db.execute("SELECT purchases.id, purchases.product_id, purchases.date AS purchase_date, purchases.quantity, purchases.purchase_price, purchases.purchase_amount, purchases.qty_after_purchase, products.product_name FROM purchases JOIN products ON purchases.product_id = products.id ORDER BY purchase_date DESC")
    for purchase in purchases:
        purchase["purchase_date_raw"] = purchase["purchase_date"]
        purchase["purchase_date"] = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d").strftime("%a, %d %b %Y")
    total_purchases = db.execute("SELECT SUM(purchases.purchase_amount) AS total_purchases FROM purchases")[0]["total_purchases"] or 0
    return render_template("purchases.html", purchases=purchases, total_purchases=total_purchases, table_id="purchasesTable")
    # Added table_id to render_template so it can be passed to the javascript file
    
@app.route("/products")
@login_required
def products():
    products = db.execute("SELECT * FROM products ORDER BY product_name ASC")
    return render_template("products.html", products=products, table_id="productsTable")


@app.route("/new_purchase", methods=["GET", "POST"])
def new_purchase():
    """Show form for adding a new purchase"""
    if request.method == "POST":
        product = request.form.get("product")
        product_id = db.execute("SELECT id FROM products WHERE product_name = ?", product)[0]["id"]
        date = request.form.get("date")
        quantity = request.form.get("purchase_quantity")
        purchase_price = request.form.get("purchase_price")
        current_quantity = db.execute("SELECT current_quantity FROM products WHERE product_name = ?", product)[0]["current_quantity"]
        restock_level = db.execute("SELECT restock_level AS restock_level FROM products WHERE product_name = ?", product)[0]["restock_level"]
        maxstock_level = db.execute("SELECT maxstocklevel AS maxstock_level FROM products WHERE product_name = ?", product)[0]["maxstock_level"]
        
        print("Product:", product)
        print("Date from form:", date)
        print("Quantity:", quantity)
        print("Price:", purchase_price)

        try:
            quantity = int(quantity)
            purchase_price = int(purchase_price)
        except ValueError:
            return apology("Quantity and purchase price must be numbers!")

        purchase_amount = quantity * purchase_price
        quantity_after_purchase = current_quantity + quantity

        if not product_id:
            return apology("Please provide a product name!")
        if not date:
            return apology("Please provide a product category!")
        elif not quantity:
            return apology("Please provide the quantity purchased!")
        elif not purchase_price:
            return apology("Please provide the purchase price!")
                
        db.execute("INSERT INTO purchases (product_id, date, quantity, purchase_price, purchase_amount, qty_after_purchase) VALUES (?, ?, ?, ?, ?, ?)", product_id, date, quantity, purchase_price, purchase_amount, quantity_after_purchase)
        db.execute("UPDATE products SET current_quantity = ? WHERE id = ?", quantity_after_purchase, product_id)
        
        
        if quantity_after_purchase <= restock_level:
            stock_status = "Needs restocking"
        elif quantity_after_purchase > maxstock_level:
            stock_status = "Overstocked"
        else:
            stock_status = "All good"

        db.execute("UPDATE products SET current_quantity = ?, stock_status = ? WHERE product_name = ?", quantity_after_purchase, stock_status, product)
        return redirect("/purchases")
    else:
        products = db.execute("SELECT product_name FROM products")
        return render_template("new_purchase.html", products=products)
    
@app.route("/new_sale", methods=["GET", "POST"])
def new_sale():
    """Show form for adding a new sale"""
    if request.method == "POST":
        product = request.form.get("product")
        product_id = db.execute("SELECT id FROM products WHERE product_name = ?", product)[0]["id"]
        date = request.form.get("date")
        quantity = request.form.get("sale_quantity")
        sale_price = request.form.get("sale_price")
        current_quantity = db.execute("SELECT current_quantity AS current_quantity FROM products WHERE product_name = ?", product)[0]["current_quantity"]
        restock_level = db.execute("SELECT restock_level AS restock_level FROM products WHERE product_name = ?", product)[0]["restock_level"]
        maxstock_level = db.execute("SELECT maxstocklevel AS maxstock_level FROM products WHERE product_name = ?", product)[0]["maxstock_level"]                                                                                                                    
        
        
        try:
            quantity = int(quantity)
            sale_price = int(sale_price)
        except ValueError:
            return apology("Quantity and sale price must be numbers!")
        
        after_sale_quantity = current_quantity - quantity
        sale_amount = quantity * sale_price

        if not product:
            return apology("Please provide a product name!")
        if not date:
            return apology("Please provide a product category!")
        elif not quantity:
            return apology("Please provide the quantity purchased!")
        elif not sale_price:
            return apology("Please provide the purchase price!")

        if after_sale_quantity == 0:
            stock_status = "Out of stock"
        elif after_sale_quantity <= restock_level:
            stock_status = "Needs restocking"
        elif after_sale_quantity > maxstock_level:
            stock_status = "Overstocked"
        else:
            stock_status = "All good"
        
        db.execute("INSERT INTO sales (product_id, date, quantity, sale_price, sale_amount, qty_after_sale) VALUES (?, ?, ?, ?, ?, ?)", product_id, date, quantity, sale_price, sale_amount, after_sale_quantity)
        db.execute("UPDATE products SET current_quantity = ?, stock_status = ? WHERE product_name = ?", after_sale_quantity, stock_status, product)
        return redirect("/")
        
    else:
        products = db.execute("SELECT * FROM products")
        return render_template("new_sale.html", products=products)
    

    
@app.route("/new_category", methods=["GET", "POST"])
def new_category():
    """Show form for adding a new category"""
    if request.method == "POST":
       
        date = request.form.get("date")
        new_category = request.form.get("new_category")
        print(new_category)
       

        if not new_category:
            return apology("Please provide a category name!")
        if not date:
            return apology("Please provide a date!")
        
                
        try:
            db.execute("INSERT INTO categories (category_name) VALUES (?)", new_category)
            
            return redirect("/")
        except:
            return apology("Category already already exists!")
    else:
        return render_template("new_category.html")
    
@app.route("/new_product", methods=["GET", "POST"])
def new_product():
    """Show form for adding a new sale"""
    if request.method == "POST":
        date = request.form.get("date")
        product = request.form.get("new_product")
        category = request.form.get("category")
        current_quantity = 0
        stock_count = 0
        stock_status = "New"
        restock_level = request.form.get("restock_level")
        maxstock_level = request.form.get("maxstock_level")
        
        try:
            restock_level = int(restock_level)
            maxstock_level = int(maxstock_level)
        except:
            return apology("Restock and/or maximum stock levels must be numbers!")


        if not date:
            return apology("Please provide a date!")
        elif not product:
            return apology("Please provide the product name!")
        elif not category:
            return apology("Please provide the product category!")
                
        try:
            db.execute(
                "INSERT INTO products (date, product_name, category, current_quantity, stock_count, restock_level, maxstocklevel, stock_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                date, product, category, current_quantity, stock_count, restock_level, maxstock_level, stock_status)
            return redirect("/")
        except Exception as e:
            return apology("Product already exists!")
    else:
        categories = db.execute("SELECT * FROM categories")
        return render_template("new_product.html", categories=categories)
    
@app.route("/other_expenses", methods=["GET", "POST"])
def other_expenses():
    """Show form for adding a new sale"""
    if request.method == "POST":
        date = request.form.get("date")
        other_expense = request.form.get("date")
        quantity = request.form.get("expense_quantity")
        expense_price = request.form.get("expense_price")
        expense_amount = quantity * expense_price

       
        if not date:
            return apology("Please provide a product category!")
        elif not other_expense:
            return apology("Please provide an expense!")
        elif not quantity:
            return apology("Please provide the quantity purchased!")
        elif not expense_price:
            return apology("Please provide the purchase price!")
                
        try:
            db.execute("INSERT INTO other_expenses (date, expense_name, quantity, expense_price, expense_amount) VALUES (?, ?, ?, ?, ?)", date, other_expense, quantity, expense_price, expense_amount)
            return redirect("/")
        except:
            return apology("Username has already been registered!")
    else:
        return render_template("other_expenses.html")
    
@app.route("/delete_product", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        delete_product = request.form.get("product")
        db.execute("DELETE FROM products WHERE product_name = ?", delete_product)
        return redirect("/products")
    else:
        products = db.execute("SELECT * FROM products")
        return render_template("delete_product.html", products=products)


if __name__ == "__main__":
    app.run(debug=True, port = 5500)