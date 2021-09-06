# Yamkela Mathontsi Class 1
import hmac
import sqlite3
import datetime
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('store.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            print(f"{data[0]}, {data[2]}, {data[3]}")
            new_data.append(User(data[0], data[2], data[3]))
    return new_data

# creating user table
def init_user_table():
    conn = sqlite3.connect("store.db")
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# creating product table
def init_product_table():
    conn = sqlite3.connect("store.db")
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS product(product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "category TEXT NOT NULL,"
                 "name TEXT NOT NULL,"
                 "price TEXT NOT NULL,"
                 "description TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


init_user_table()
init_product_table()
users = fetch_users()

username_table = { u.username: u for u in users }
userid_table = { u.id: u for u in users }


# users authentication
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


# email verification
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=4000)
CORS(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "yamkelapj@gmail.com"
app.config['MAIL_PASSWORD'] = "#Godisgood7"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

jwt = JWT(app, authenticate, identity)

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

# new users registration
@app.route('/user-registration/', methods=["POST"])
def registration():
    response = {}

    if request.method == "POST":

        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form ['email']

        with sqlite3.connect("store.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "name,"
                           "username,"
                           "password) VALUES(?, ?, ?)", (name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
            if response["status_code"] == 201:
                msg = Message('Welcome Message', sender='lottoyamkela@gmail.com',
                              recipients=[email])
                msg.body = "Welcome, You have successfully registered ."
                mail.send(msg)
            return "Email Sent To User"

        return response


# registered users login
@app.route("/login/", methods=["POST"])
def login():
    response = {}

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("store.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE username='{}' AND password='{}'".format(username, password))
            user_information = cursor.fetchone()

        if user_information:
            response["user_info"] = user_information
            response["message"] = "Success"
            response["status_code"] = 201
            return jsonify(response)

        else:
            response['message'] = "Unsuccessful login, try again"
            response['status_code'] = 401
            return jsonify(response)


# adding more products to your cart
@app.route('/adding/', methods=["POST"])
def add_products():
    response = {}

    if request.method == "POST":
        category = request.form['category']
        name = request.form["name"]
        price = request.form['price']
        description = request.form['description']

        with sqlite3.connect("store.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO product("
                           "category,"
                           "name,"
                           "price,"
                           "description) VALUES(?, ?, ?, ?)", (category, name, price, description))
            connection.commit()
            response["message"] = "product added successfully"
            response["status_code"] = 201
        return response


# viewing products in your cart
@app.route('/view/')
def view_products():
    response = {}

    with sqlite3.connect("store.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM product")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


# decided to change a product, updating or changing a product in your cart
@app.route('/changing/<int:product_id>/', methods=["PUT"])
def updating_products(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('store.db') as conn:
            print(request.json)
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("category") is not None:
                put_data["category"] = incoming_data.get("category")
                response['message'] = "product update was successful"
                response['status_code'] = 200

                with sqlite3.connect('store.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE product SET category =? WHERE product_id=?", (put_data["category"],
                                                                                              product_id))
            elif incoming_data.get("name") is not None:
                put_data["name"] = incoming_data.get("name")
                response['message'] = "product update was successful"
                response['status_code'] = 200

                with sqlite3.connect('store.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE product SET name =? WHERE product_id=?",
                                   (put_data["name"], product_id))

                    conn.commit()
                    response['message'] = "product update was successful"
                    response['status_code'] = 200

    return response

# edita product
@app.route('/edit-product/<int:product_id>/', methods=["PUT"])
@jwt_required()
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('store.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("title") is not None:
                put_data["title"] = incoming_data.get("title")
                with sqlite3.connect('store.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET title =? WHERE id=?", (put_data["title"], product_id))
                    conn.commit()
                    response['message'] = "title update was successful"
                    response['status_code'] = 200
            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('store.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET description =? WHERE id=?", (put_data["description"], product_id))
                    conn.commit()

                    response["description"] = "description update was successful"
                    response["status_code"] = 200
            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('store.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET price =? WHERE id=?", (put_data["price"], product_id))
                    conn.commit()

                    response["price"] = "price update was successful"
                    response["status_code"] = 200
            if incoming_data.get("category") is not None:
                put_data['category'] = incoming_data.get('category')

                with sqlite3.connect('store.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET category =? WHERE id=?", (put_data["category"], product_id))
                    conn.commit()

                    response["category"] = "category update was successful"
                    response["status_code"] = 200
    return response


# decided to get a better product, deleting a product in your cart
@app.route('/delete/<int:product_id>/')
def delete_products(product_id):
    response = {}

    with sqlite3.connect("store.db") as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM product WHERE product_id=" + str(product_id))
        connection.commit()
        response['status_code'] = 200
        response['message'] = "Product successfully removed from your basket."
    return response


if __name__ == "__main__":
    app.debug = True
    app.run(port=5000)

