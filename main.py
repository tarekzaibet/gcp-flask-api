import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flasgger import Swagger

from src.api import api_mock_blueprint, api_v1_blueprint, api_v1
from src.services import oauth2_flow
from src.services.storage import get_content_to_file

app = Flask(__name__)

with open("src/swagger/template.json") as data_file:
    template = json.load(data_file)


# set config mode to dev

config_mode = 'src.config.DevelopmentConfig'
app.config.from_object(config_mode)

# register blueprints
CORS(app)
app.register_blueprint(api_mock_blueprint)
app.register_blueprint(api_v1_blueprint)

get_content_to_file("gcp-flask-api","client_secret_creation_form.json")


@app.route('/', methods=['GET', 'POST'])
def index():

    return jsonify({"message": "ok"})



@app.route('/oauth2callback', methods=['POST'])
def auth_code():
    auth_code = oauth2_flow.extract_auth_code(request)

    access_token = oauth2_flow.authenticate_using_auth_code(auth_code)
    print('access_token ({}): {}'.format(type(access_token), access_token))

    # TODO: replace access_token with BasicProfile
    return jsonify(access_token)


if __name__ == "__main__":
    import os
    ##app.run(host='127.0.0.1', port=8080, debug=True)
    app.run(host='localhost', port=5000,debug=True)
    os.environ.set('DEBUG', 'yes')
