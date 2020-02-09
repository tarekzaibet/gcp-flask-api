from flask import request, jsonify

class EntityNotFound(Exception):
    pass


def make_error(status_code, sub_code, message):
    response = jsonify({
        'status': status_code,
        'sub_code': sub_code,
        'message': message,
    })
    response.status_code = status_code
    return response
