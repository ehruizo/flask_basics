"""
GET http://127.0.0.1:5000/
GET http://127.0.0.1:5000/read
POST http://127.0.0.1:5000/create
UPDATE http://127.0.0.1:5000/update
DELETE http://127.0.0.1:5000/delete
GET http://127.0.0.1:5000/form
GET http://127.0.0.1:5000/json
"""
from flask import Flask, render_template, request, jsonify


app = Flask(__name__)


# GET REQUEST
@app.route('/')
def index():
    return 'Hello there!'


@app.route('/read')
def get_req():
    return "Hi, I got your GET Request!"


# POST REQUEST
@app.route('/create', methods=['POST'])
def post_req():
    return "I see you sent a POST message :-)"


# UPDATE REQUEST
@app.route('/update', methods=['PUT'])
def update_req():
    return "Sending Hello on an PUT request!"


# DELETE REQUEST
@app.route('/delete', methods=['DELETE'])
def delete_req():
    return "Deleting your hard drive.....haha just kidding! I received a DELETE request!"


# RENDER TEMPLATE (html in templates folder by default)
@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    email = request.form['email']
    site = request.form['site_url']
    comments = request.form['comments']
    return render_template('submitted_form.html', name=name, email=email, site=site, comments=comments)


# JSON RESPONSE
@app.route("/json")
def json_test():
    return jsonify(message="hola, cómo le va?")


if __name__ == '__main__':
    app.run(debug=True, port=5000)
