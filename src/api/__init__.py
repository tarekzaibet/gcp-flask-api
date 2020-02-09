from flask import Blueprint
from flask_restful import Api

from src.api.projects import *

api_v1_blueprint = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v1 = Api(api_v1_blueprint)


# project endpoints
api_v1.add_resource(DeployProjectEndpoint, '/deploy/project')
api_v1.add_resource(GetProjectsInfoEndpoint, '/projects')
api_v1.add_resource(GetProjectInfoEndpoint, '/project/<string:project_id>')
api_v1.add_resource(GetProjectPolicyEndpoint, '/project/policy/<string:project_id>')
api_v1.add_resource(AddUserToProjectPolicyEndpoint, '/project/user/add/<string:project_id>/<string:member_id>/<string:role>')
api_v1.add_resource(RemoveUserFromProjectPolicyEndpoint, '/project/user/remove/<string:project_id>/<string:member_id>')


# Mocks
api_mock_blueprint = Blueprint('api_mock', __name__, url_prefix='/api/mock')
api_mock = Api(api_mock_blueprint)


