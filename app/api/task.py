  
from flask import (
    Blueprint, g, request, abort, jsonify
)
from passlib.hash import pbkdf2_sha256
import jwt
from flask_jwt_extended import (
    jwt_required, create_access_token, get_current_user
)
import re
from bson.objectid import ObjectId
import requests
import datetime
from app import mongo
from app import token
import dateutil.parser
import json
from bson import json_util
from passlib.apps import custom_app_context as pwd_context

bp = Blueprint('task', __name__, url_prefix='/')




@bp.route('/register', methods=['POST'])
def register():
   name = request.json.get("name", None)
   username = request.json.get("username", None)
   password = request.json.get("password", None)
   if not name or not username or not password:
       return jsonify({"msg": "Invalid Request"}), 400

   user = mongo.db.users.count({
       "username": username
   })
   if user > 0:
       return jsonify({"msg": "Username already taken"}), 500

   id = mongo.db.users.insert_one({
       "name": name,
       "password": pbkdf2_sha256.hash(password),
       "username": username
   }).inserted_id
   return jsonify(str(id))




@bp.route('/login', methods=['POST'])
def login():
    log_username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not log_username:
        return jsonify(msg="Missing username parameter"), 400
    if not password:
        return jsonify(msg="Missing password parameter"), 400

    is_user = mongo.db.users.find_one({"username": log_username})
    if is_user is None:
        return jsonify(msg="username doesn't exists"), 400

    if not pbkdf2_sha256.verify(password, is_user["password"]):
        return jsonify(msg="password is wrong"), 400
    username1 = log_username
    expires = datetime.timedelta(days=1)
    access_token = create_access_token(identity=username1, expires_delta=expires)
    return jsonify(access_token=access_token), 200


  
@bp.route('/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_current_user()
    current_user["_id"] = str(current_user["_id"])
    user = json.dumps(current_user,default=json_util.default)
    return user, 200


@bp.route('/profile', methods=['PUT', 'GET'])
@jwt_required
def profile():
    current_user = get_current_user()
    if request.method == "GET":
        ret = mongo.db.users.find_one({
            "_id": ObjectId(current_user["_id"])
        })
        return jsonify(ret)

    if request.json is None:
        abort(500)
    ret = mongo.db.users.update({
        "_id": ObjectId(current_user["_id"])
    }, {
        "$set": {
            "profile": request.json
        }
    })
    return jsonify(str(ret)), 200

