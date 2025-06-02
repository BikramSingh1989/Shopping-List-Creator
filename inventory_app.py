import pymongo
import bcrypt
from getpass import getpass

# MongoDB Connection
client = pymongo.MongoClient("mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority")
db = client.inventoryApp
users_col = db.users
items_col = db.items

# Helper functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# User Authentication
def register():
    username = input("Enter new username: ")
    if users_col.find_one({"username": username}):
        print("Username already exists.")
        return None
    password = getpass("Enter new password: ")
    users_col.insert_one({"username": username, "password": hash_password(password)})
    print("Registered successfully!")
    return username

def login():
    username = input("Enter username: ")
    user = users_col.find_one({"username": username})
    if not user:
        print("User not found.")
        return None
    password = getpass("Enter password: ")
    if verify_password(password, user["password"]):
        print("Login successful!")
        return username
    else:
        print("Incorrect password.")
        return None

# Inventory Operations
def add_item(username):
    name = input("Item name: ")
    qty = int(input("Inventory on hand: "))
    par = int(input("Par level: "))
    items_col.insert_one({"user": username, "name": name, "quantity": qty, "par": par})
    print("Item added.")

def view_inventory(username):
    print("Current Inventory:")
    for item in items_col.find({"user": username}):
        print(f"- {item['name']}: {item['quantity']} (Par: {item['par']})")

def update_item(username):
    name = input("Item name to update: ")
    item = items_col.find_one({"user": username, "name": name})
    if not item:
        print("Item not found.")
        return
    new_qty = int(input("New quantity: "))
    items_col.update_one({"_id": item["_id"]}, {"$set": {"quantity": new_qty}})
    print("Item updated.")

def delete_item(username):
    name = input("Item name to delete: ")
    result = items_col.delete_one({"user": username, "name": name})
    print("Item deleted." if result.deleted_count else "Item not found.")

def generate_shopping_list(username):
    print("Shopping List (Items below Par):")
    for item in items_col.find({"user": username, "$expr": {"$lt": ["$quantity", "$par"]}}):
        needed = item["par"] - item["quantity"]
        print(f"- {item['name']} (Need: {needed})")

# App Menu
def run_app():
    print("Welcome to the Inventory App")
    user = None
    while not user:
        action = input("Do you want to [login], [register], or [quit]? ").lower()
        if action == "login":
            user = login()
        elif action == "register":
            user = register()
        elif action == "quit":
            return

    while True:
        print("\nOptions: [add], [view], [update], [delete], [shopping], [logout]")
        choice = input("Choose an action: ").lower()
        if choice == "add":
            add_item(user)
        elif choice == "view":
            view_inventory(user)
        elif choice == "update":
            update_item(user)
        elif choice == "delete":
            delete_item(user)
        elif choice == "shopping":
            generate_shopping_list(user)
        elif choice == "logout":
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    run_app()
