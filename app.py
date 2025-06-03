from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timezone
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri or not mongo_uri.startswith(("mongodb://", "mongodb+srv://")):
    raise ValueError("Invalid or missing MONGO_URI.")

client = MongoClient(mongo_uri)
db = client.inventory_app
users_col = db.users

@app.route("/")
def index():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if users_col.find_one({'username': username}):
            return "User already exists"
        users_col.insert_one({'username': username, 'password': password, 'items': []})
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = users_col.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect("/dashboard")
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'username' not in session:
        return redirect("/login")

    user = users_col.find_one({'username': session['username']})

    if request.method == "POST":
        item_id = request.form.get('item_id')
        name = request.form['name']
        category = request.form['category']
        expiration_str = request.form.get('expiration')

        try:
            quantity = int(request.form['quantity'])
            par = int(request.form['par'])
            if quantity > 9999 or par > 9999:
                return "Error: Quantity and stock level must be less than 10,000."
        except ValueError:
            return "Error: Please enter valid numbers for quantity and stock level."

        expiration_date = None
        if expiration_str:
            try:
                expiration_date = datetime.strptime(expiration_str, '%Y-%m-%d')
            except ValueError:
                return "Invalid expiration date format (expected YYYY-MM-DD)"

        item_data = {
            'name': name,
            'quantity': quantity,
            'par': par,
            'category': category,
            'expiration': expiration_date
        }

        if item_id:
            users_col.update_one(
                {'_id': user['_id'], 'items._id': ObjectId(item_id)},
                {'$set': {f'items.$.{k}': v for k, v in item_data.items()}}
            )
        else:
            item_data['_id'] = ObjectId()
            users_col.update_one({'_id': user['_id']}, {'$push': {'items': item_data}})

        return redirect("/dashboard")

    items = user.get('items', [])
    now = datetime.now()

    for item in items:
        exp = item.get('expiration')
        if exp:
            try:
                delta = (exp - now).days
                item['days_left'] = delta
            except Exception:
                item['days_left'] = None
        else:
            item['days_left'] = None

    shopping_list = [item for item in items if item['quantity'] < item['par']]
    return render_template("dashboard.html", items=items, shopping=shopping_list, now=now)

@app.route("/delete/<item_id>")
def delete(item_id):
    if 'username' not in session:
        return redirect("/login")
    users_col.update_one(
        {'username': session['username']},
        {'$pull': {'items': {'_id': ObjectId(item_id)}}}
    )
    return redirect("/dashboard")

@app.route("/edit/<item_id>")
def edit_item(item_id):
    if 'username' not in session:
        return redirect("/login")

    user = users_col.find_one({'username': session['username']})
    item = next((item for item in user.get('items', []) if str(item['_id']) == item_id), None)

    if not item:
        return "Item not found"

    return render_template("edit_item.html", item=item)

@app.route("/clear-inventory")
def clear_inventory():
    if 'username' in session:
        users_col.update_one({'username': session['username']}, {'$set': {'items': []}})
    return redirect("/dashboard")

@app.route("/shopping-list")
def shopping_list():
    if 'username' not in session:
        return redirect("/login")

    user = users_col.find_one({'username': session['username']})
    items = user.get('items', [])
    shopping = [item for item in items if item['quantity'] < item['par']]
    return render_template("shopping_list.html", shopping=shopping)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/login")

@app.route("/how-to-use")
def how_to_use():
    return render_template("how_to_use.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
