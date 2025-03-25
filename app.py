import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
    return render_template("index.html")
    
    
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
    return redirect("/")

@app.route("/sales")
@login_required
def sales():
    sales = db.execute("SELECT sales.date, products.product_name, sales.quantity, sales.sale_price, sales.sale_amount FROM sales JOIN products ON sales.product_id = products.id")
    print(sales)
    return render_template("sales.html", sales=sales)
    
if __name__ == "__main__":
    app.run(debug=True)


@app.route("/purchase", methods=["GET", "POST"])
def new_purchase():
    """Register user"""
    if request.method == "POST":
        product = request.form.get("product")
        product_id = db.execute("SELECT id FROM products WHERE product_name = ?", product)
        date = request.form.get("date")
        quantity = request.form.get("purchase_quantity")
        purchase_price = request.form.get("purchase_price")
        purchase_amount = quantity * purchase_price

        if not product_id:
            return apology("Please provide a product name!")
        if not date:
            return apology("Please provide a product category!")
        elif not quantity:
            return apology("Please provide the quantity purchased!")
        elif not purchase_price:
            return apology("Please provide the purchase price!")
                
        try:
            db.execute("INSERT INTO purchases (product_id, date, quantity, purchase_price, purchase_amount) VALUES (?, ?, ?, ?, ?)", product_id, date, quantity, purchase_price, purchase_amount)
            return redirect("/")
        except:
            return apology("Username has already been registered!")
    else:
        return render_template("purchase.html")