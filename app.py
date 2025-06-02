from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
import bcrypt
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = '15e0bcdf3bff4760a718bd37bbacd103'  

# MongoDB Setup
client = pymongo.MongoClient("mongodb+srv://user:testpassword@shopping-list-creator.3r3nujk.mongodb.net/")
db = client.inventoryApp
users_col = db.users
items_col = db.items

# Routes
@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = users_col.find_one({'username': request.form['username']})
        if user and bcrypt.checkpw(request.form['password'].encode('utf-8'), user['password']):
            session['username'] = user['username']
            return redirect('/dashboard')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if users_col.find_one({'username': request.form['username']}):
            return render_template('register.html', error='Username already exists')
        hashed = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        users_col.insert_one({'username': request.form['username'], 'password': hashed})
        return redirect('/login')
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        items_col.insert_one({
            'user': session['username'],
            'name': request.form['name'],
            'quantity': int(request.form['quantity']),
            'par': int(request.form['par'])
        })
    items = list(items_col.find({'user': session['username']}))
    shopping_list = [item for item in items if item['quantity'] < item['par']]
    return render_template('dashboard.html', items=items, shopping=shopping_list)

@app.route('/delete/<item_id>')
def delete_item(item_id):
    items_col.delete_one({'_id': ObjectId(item_id)})
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
