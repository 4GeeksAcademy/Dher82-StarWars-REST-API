"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorites
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# INICIO DE CÓDIGO
# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():
    # DEBERÍA TRAERME TODOS LOS USUARIOS

    # response_body = {
    #     "msg": "Debería trarme todos los usuarios. Hello, this is your GET /user response "
    # }

    all_users = User.query.all()
    print(all_users)
    result = list(map(lambda user: user.serialize(), all_users))
    print(result)

    return jsonify(result), 200


@app.route('/user/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": f"user with id {user_id} not found"}), 404
    serialized_user = user.serialize()
    return serialized_user, 200


@app.route('/character', methods=['GET'])
def get_character():
    all_character = Character.query.all()
    result = list(map(lambda item: item.serialize(), all_character))

    return jsonify(result), 200


@app.route('/character/<int:character_id>', methods=['GET'])
def get_one_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"msg": f"character with id {character_id} not found"}), 404
    serialized_character = character.serialize()
    return serialized_character, 200

# planets


@app.route('/planet', methods=['GET'])
def get_planet():
    all_planet = Planet.query.all()
    result = list(map(lambda item: item.serialize(), all_planet))

    return jsonify(result), 200


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": f"planet with id {planet_id} not found"}), 404
    serialized_planet = planet.serialize()
    return serialized_planet, 200


@app.route('/user', methods=['POST'])
def create_one_user():
    body = json.loads(request.data)
    new_user = User(
        email=body["email"],
        password=body["password"],
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "user created succesfull"}), 200


@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['POST'])
def create_one_favorite_planet(planet_id, user_id):
    fav_user = Favorites.query.filter_by(id_user=user_id).first()
    fav_id = Favorites.query.filter_by(planet_id=planet_id).first()

    if fav_user and not fav_id:
        new_favorite = Favorites(id_user=user_id, planet_id=planet_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"msg": "Favorito creado"}), 200

    return jsonify({"msg": "Este planeta ya es favorito para ese usuario" if fav_id else "No existe el usuario"}), 400

# acá viene favorite people o character --- a partir de acá continué hasta la línea 146


@app.route('/favorite/character/<int:character_id>/<int:user_id>', methods=['POST'])
def create_one_favorite_character(character_id, user_id):
    fav_user = Favorites.query.filter_by(id_user=user_id).first()
    fav_id = Favorites.query.filter_by(character_id=character_id).first()

    if fav_user and not fav_id:
        new_favorite = Favorites(id_user=user_id, character_id=character_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"msg": "Favorito creado"}), 200

    return jsonify({"msg": "Este personaje ya es favorito para ese usuario" if fav_id else "No existe el usuario"}), 400


@app.route('/favorite/planet/<int:planets_id>', methods=['DELETE'])
def delete_one_favorite_planet(planets_id):
    delete_favorite_planet = Favorites.query.get(planets_id)
    db.session.delete(delete_favorite_planet)
    db.session.commit()
    return jsonify({"msg": "Favorite planet deleted succesfully"}), 200

# DELETE DE CHARACTER


@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_one_favorite_character(character_id):
    delete_favorite_character = Favorites.query.get(character_id)
    db.session.delete(delete_favorite_character)
    db.session.commit()
    return jsonify({"msg": "Favorite character deleted succesfully"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
