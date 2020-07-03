import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# CORS Headers
@app.after_request
def after_request(response):
    # response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,POST,PATCH,DELETE')
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

db_drop_and_create_all()


# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks():
    payload = get_payload(request)

    check_valid_payload(payload)
    check_unique_title(payload)

    drink = Drink(title=payload['title'], recipe=payload['recipe'])
    drink.insert()

    return jsonify({
        "success": True,
        "drinks": [drink.short()]
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(drink_id):
    payload = get_payload(request)

    check_drink_exist(drink_id)
    check_valid_payload(payload)

    drink = Drink.query.get(drink_id)
    drink.title = payload['title']
    drink.recipe = payload['recipe']
    drink.update()

    drinks = [drink.long()]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(drink_id):
    check_drink_exist(drink_id)

    drink = Drink.query.get(drink_id)
    drink.delete()

    return jsonify({
        "success": True,
        "delete": drink_id
    })


def get_payload(request):
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    return {
        'title': new_title,
        'recipe': json.dumps(new_recipe) if new_recipe is not None else None
    }


def check_valid_payload(payload):
    if payload['title'] is None or payload['recipe'] is None:
        abort(400)


def check_unique_title(payload):
    if Drink.query.filter_by(title=payload['title']).count() > 0:
        abort(422)


def check_drink_exist(drink_id):
    if Drink.query.filter_by(id=drink_id).count() < 1:
        abort(404)


# Error Handling


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


# @app.errorhandler(Exception)
# def handle_exception(error):
#     print(error)
#     return jsonify({
#         "success": False,
#         "error": 500,
#         "message": "internal server error"
#     }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def handle_auth_error(error):
    message = {
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden'
    }
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": message[error.status_code],
        "code": error.error['code'],
        "description": error.error['description']
    }), error.status_code
