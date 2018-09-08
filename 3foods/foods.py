"""
---
API con autenticación con token
---
GET http://localhost:5000/hello  --  error
POST http://localhost:5000/users | {"username": "pedro", "password": "1234"} | application/json  --  ok
GET http://localhost:5000/users/1  --  ok
GET http://localhost:5000/login | Basic Auth  --  ok
GET http://localhost:5000/hello | Basic Auth (token, "") --  ok
GET http://localhost:5000/products/vegetable | Basic Auth (token, "") --  ok
GET http://localhost:5000/products/flesh | Basic Auth (token, "") --  error
POST http://localhost:5000/products | {"name": "betabel", "category": "vegetable", "price": "$ 2.00"} | Basic Auth (token, "") --  ok
GET http://localhost:5000/products | Basic Auth (token, "") --  ok
GET http://localhost:5000/products | Basic Auth (pedro, 1234) --  ok
"""
from models import User, Product, engine, init_db
from flask import Flask, jsonify, request, abort, g
from sqlalchemy.orm import sessionmaker
from flask_httpauth import HTTPBasicAuth


# crea la base de datos si no existe
init_db()

app = Flask(__name__)

DBSession = sessionmaker(bind=engine)
session = DBSession()

auth = HTTPBasicAuth()


# esto no está bien implementado, ya que acepta Basic Auth en los endpoints que solo deberían aceptar token
# se debería modificar para aceptar Basic Auth solo en el login y token en los demás
@auth.verify_password
def verify_password(username_or_token, password):
    # el token se recibe en el campo del usuario del Basic Auth, la contraseña no importa
    user_id, expired = User.verify_auth_token(username_or_token)
    if expired:
        print("Expired token")
        return False
    elif user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(username=username_or_token).first()
        if not user:
            print("User not found")
            return False
        elif not user.verify_password(password):
            print("Wrong password")
            return False
    g.user = user
    return True


@app.route('/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print("missing arguments")
        abort(400) 
    if session.query(User).filter_by(username=username).first() is not None:
        print("existing user")
        return jsonify(error='user already exists')
    user = User(username=username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify(user.serialize), 201


@app.route('/users/<int:uid>')
def get_user(uid):
    try:
        user = session.query(User).filter_by(id=uid).one()
        return jsonify(user.serialize)
    except:
        abort(400)


@app.route('/login')
@auth.login_required
def get_token():
    token = g.user.generate_auth_token()
    return jsonify(token=token.decode('utf-8'))


@app.route('/hello')
@auth.login_required
def get_resource():
    return jsonify(data='Hello, {}!'.format(g.user.username))


@app.route('/products', methods=['GET', 'POST'])
@auth.login_required
def show_all_products():
    if request.method == 'GET':
        products = session.query(Product).all()
        return jsonify(products=[p.serialize for p in products])
    if request.method == 'POST':
        name = request.json.get('name')
        category = request.json.get('category')
        price = request.json.get('price')
        if not name or not category or not price:
            return jsonify(error="faltan campos")
        new_item = Product(name=name, category=category, price=price)
        session.add(new_item)
        session.commit()
        return jsonify(new_item.serialize)


@app.route('/products/<category>')
@auth.login_required
def show_products_in_category(category):
    if category in ('fruit', 'legume', 'vegetable'):
        fruit_items = session.query(Product).filter_by(category=category).all()
        return jsonify(category=category, products=[f.serialize for f in fruit_items])
    else:
        return jsonify(error="invalid category, must be fruit, legume or vegetable")
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
