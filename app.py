from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

client = MongoClient(os.getenv("MONGO_URI"))
db = client.inventory_app
users_col = db.users

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
        name = request.form['name']
        quantity = int(request.form['quantity'])
        par = int(request.form['par'])
        expiration_str = request.form.get('expiration')

        expiration_date = None
        if expiration_str:
            try:
                expiration_date = datetime.strptime(expiration_str, '%Y-%m-%d')
            except ValueError:
                expiration_date = None

        users_col.update_one(
            {'_id': user['_id']},
            {'$push': {'items': {
                'name': name,
                'quantity': quantity,
                'par': par,
                'expiration': expiration_date
            }}}
        )
        return redirect("/dashboard")

    items = user.get('items', [])
    shopping_list = [item for item in items if item['quantity'] < item['par']]

    return render_template("dashboard.html", items=items, shopping=shopping_list)

@app.route("/delete/<item_id>")
def delete(item_id):
    if 'username' not in session:
        return redirect("/login")

    users_col.update_one(
        {'username': session['username']},
        {'$pull': {'items': {'_id': ObjectId(item_id)}}}
    )
    return redirect("/dashboard")

@app.route("/clear-inventory")
def clear_inventory():
    if 'username' in session:
        users_col.update_one(
            {'username': session['username']},
            {'$set': {'items': []}}
        )
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/login")

@app.route("/how-to-use")
def how_to_use():
    return render_template("how_to_use.html")

if __name__ == "__main__":
    app.run(debug=True)