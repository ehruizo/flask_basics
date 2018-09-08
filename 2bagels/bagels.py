"""
---
API con Autenticación Básica
---
GET http://localhost:5000/hello  --  error
POST http://localhost:5000/users | {"username": "pedro"} | application/json  --  error
POST http://localhost:5000/users | {"username": "pedro", "password": "1234"} | application/json  --  ok
POST http://localhost:5000/users | {"username": "pedro", "password": "12345"} | application/json  --  error
GET http://localhost:5000/users/2  --  ok
GET http://localhost:5000/users/50  --  error
GET http://localhost:5000/hello | Basic Auth  --  ok
POST http://localhost:5000/bagels | {"price": 5} | Basic Auth | application/json  --  error
POST http://localhost:5000/bagels | {"name": "coconut", "price": 5, "description": "coconut bagel"} | Basic Auth | application/json  --  ok
GET http://localhost:5000/bagels  --  error
GET http://localhost:5000/bagels | Basic Auth  --  ok
"""
from models import User, Bagel, engine, init_db
from flask import Flask, jsonify, request, abort, g
from sqlalchemy.orm import sessionmaker
from flask_httpauth import HTTPBasicAuth


# crea la base de datos si no existe
init_db()

app = Flask(__name__)

DBSession = sessionmaker(bind=engine)
session = DBSession()

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    print("Looking for user {}".format(username))
    user = session.query(User).filter_by(username=username).first()
    if not user:
        print("User not found")
        return False
    elif not user.verify_password(password):
        print("Wrong password")
        return False
    else:
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
        return jsonify(error='user already exists'), 200
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


@app.route('/hello')
@auth.login_required
def get_resource():
    return jsonify(data='Hello, {}!'.format(g.user.username))


@app.route('/bagels', methods=['GET', 'POST'])
@auth.login_required
def show_all_bagels():
    if request.method == 'GET':
        bagels = session.query(Bagel).all()
        return jsonify(bagels=[bagel.serialize for bagel in bagels])
    elif request.method == 'POST':
        name = request.json.get('name')
        if name is None:
            return jsonify(error="Name missing")
        description = request.json.get('description')
        picture = request.json.get('picture')
        price = request.json.get('price')
        new_bagel = Bagel(name=name, description=description, picture=picture, price=price)
        session.add(new_bagel)
        session.commit()
        return jsonify(new_bagel.serialize)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
