"""
API con flujo de autenticación OAuth 2, usando a Google como servidor de autenticación
"""
from models import User, engine, init_db
from flask import Flask, jsonify, request, abort, g, render_template, make_response
from sqlalchemy.orm import sessionmaker
from flask_httpauth import HTTPBasicAuth
import json
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import requests


init_db()

DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
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


@app.route('/clientOAuth')
def start():
    return render_template('clientOAuth.html')


@app.route('/oauth/<provider>', methods=['POST'])
def login(provider):
    # STEP 1 - Parse the auth code
    auth_code = request.json.get('auth_code')
    print("Step 1 - Complete, received auth code {}".format(auth_code))
    if provider == 'google':
        # STEP 2 - Exchange for a token
        try:
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
          
        # Check that the access token is valid.
        access_token = credentials.access_token
        url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'.format(access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        # # Verify that the access token is used for the intended user.
        # gplus_id = credentials.id_token['sub']
        # if result['user_id'] != gplus_id:
        #     response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        #     response.headers['Content-Type'] = 'application/json'
        #     return response

        # # Verify that the access token is valid for this app.
        # if result['issued_to'] != CLIENT_ID:
        #     response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        #     response.headers['Content-Type'] = 'application/json'
        #     return response

        # stored_credentials = login_session.get('credentials')
        # stored_gplus_id = login_session.get('gplus_id')
        # if stored_credentials is not None and gplus_id == stored_gplus_id:
        #     response = make_response(json.dumps('Current user is already connected.'), 200)
        #     response.headers['Content-Type'] = 'application/json'
        #     return response

        print("Step 2 Complete! Access Token : {}".format(credentials.access_token))

        # STEP 3 - Find user or make a new one
        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)
      
        data = answer.json()
        name = data['name']
        picture = data['picture']
        email = data['email']

        # see if user exists, if it doesn't make a new one
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username=name, picture=picture, email=email)
            session.add(user)
            session.commit()

        # STEP 4 - Make own token
        token = user.generate_auth_token(600)

        # STEP 5 - Send back token to the client
        return jsonify(token=token.decode('utf-8'))

    else:

        return jsonify(error='Unrecognized Provider')


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


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


@app.route('/api/users/<int:uid>')
def get_user(uid):
    user = session.query(User).filter_by(id=uid).one()
    if not user:
        abort(400)
    return jsonify(user.serialize)


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify(data='Hello, %s!'.format(g.user.username))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
