"""
API Básica
"""
from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from models import Puppy, engine, init_db


# crea la base de datos si no existe
# esto se debe ejecutar una sola vez, por lo que en realidad no debería ir acá sino en un archivo de inicialización
# que se ejecuta al instalar la app (también se puede ejecutar init_db() manualmente)
init_db()

app = Flask(__name__)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route("/json")
def jsonTest():
    return jsonify(message="hola")


@app.route("/")
@app.route("/puppies", methods=["GET", "POST"])
def puppiesFunction():
    if request.method == "GET":
        return getAllPuppies()
    elif request.method == "POST":
        print("Making a New puppy")
        name = request.args.get('name', '')                  # parámetros GET
        description = request.args.get('description', '')
        print(name)
        print(description)
        return makeANewPuppy(name, description)


@app.route('/puppies/<int:pid>', methods=["GET", "PUT", "DELETE"])
def puppiesFunctionId(pid):
    if request.method == "GET":
        return getPuppy(pid)
    elif request.method == "PUT":
        name = request.args.get('name', '')                 # parámetros GET
        description = request.args.get('description', '')
        return updatePuppy(pid, name, description)
    elif request.method == "DELETE":
        return deletePuppy(pid)


def getAllPuppies():
    puppies = session.query(Puppy).all()
    return jsonify(Puppies=[i.serialize for i in puppies])


def getPuppy(pid):
    puppy = session.query(Puppy).filter_by(id=pid).one()
    return jsonify(puppy=puppy.serialize)


def makeANewPuppy(name, description):
    puppy = Puppy(name=name, description=description)
    session.add(puppy)
    session.commit()
    return jsonify(Puppy=puppy.serialize)


def updatePuppy(pid, name, description):
    puppy = session.query(Puppy).filter_by(id=pid).one()
    if name:
        puppy.name = name
    if description:
        puppy.description = description
    session.add(puppy)
    session.commit()
    return "Updated a Puppy with id {}".format(pid)


def deletePuppy(pid):
    puppy = session.query(Puppy).filter_by(id=pid).one()
    session.delete(puppy)
    session.commit()
    return "Removed Puppy with id {}".format(pid)


if __name__ == '__main__':
    app.run(debug=True, port=5000)

