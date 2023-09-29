from flask import Blueprint, jsonify
import json

view_json_blueprint = Blueprint('view_json', __name__)

@view_json_blueprint.route('/get-json')
def get_json():
    with open('users.json', 'r') as file:
        data = json.load(file)
    return jsonify(data)
